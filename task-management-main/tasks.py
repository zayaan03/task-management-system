import datetime as dt
from datetime import timedelta
import pytz
from database import Database
from collections import defaultdict

PK_TZ = pytz.timezone("Asia/Karachi")


class Task:
    """Represents a single task."""

    def __init__(self, task_id, user_id, title, description, priority, due_date, status):
        self.task_id    = task_id
        self.user_id    = user_id
        self.title      = title
        self.description = description
        self.priority   = priority
        self.due_date   = due_date
        self.status     = status

    def __repr__(self):
        return f"Task(id={self.task_id}, title='{self.title}', status='{self.status}')"


class Subtask_Item:

    """Represents a single checklist item inside a task."""

    def __init__(self, item_id, task_id, title, is_done):
        self.item_id  = item_id
        self.task_id  = task_id
        self.title    = title
        self.is_done  = bool(is_done)

    def __repr__(self):
        return f"ChecklistItem(id={self.item_id}, title='{self.title}', done={self.is_done})"



class TaskManagement:

    """Handles all task CRUD with tasks table"""

    VALID_PRIORITIES = ("Low", "Normal", "High", "Urgent")

    def __init__(self, db = Database()):
        self.client = db.get_client()

    def get_tasks(self, user_id: str) -> list:

        """Fetch all tasks for a user. Returns list of Task objects."""
        
        response = (
            self.client.table('tasks')
            .select('task_id, task_title, task_priority, due_date, task_status')
            .eq('user_id', user_id)
            .execute()
        )

        return [
            Task(
                task_id     = row['task_id'],
                user_id     = user_id,
                title       = row['task_title'],
                description = None,
                priority    = row['task_priority'],
                due_date    = row['due_date'],
                status      = row['task_status']
            )
            for row in response.data
        ]

    def create_task(self, user_id: str, title: str, description: str,
                    priority: str, due_date, status: str):

        """Add new task to the database for authenticated user"""

        if not priority:
            priority = 'Normal'

        response = (
            self.client.table('tasks')
            .insert({
                'user_id': user_id,
                'task_title': title,
                'task_description': description,
                'task_priority'    : priority,
                'due_date': str(due_date),
                'task_status': status
            })
            .execute()
        )

        return response.data[0]['task_id'] if response.data else None

    def get_task_by_id(self, task_id: str, user_id: str):
        
        """Fetch a single task using id for editing."""

        response = (
            self.client.table('tasks')
            .select('task_id, task_title, task_description, task_priority, due_date, task_status')
            .eq('task_id', task_id)
            .eq('user_id', user_id)
            .execute()
        )

        if not response.data:
            return None

        row = response.data[0]
        return Task(
            task_id    = row['task_id'],
            user_id     = user_id,
            title       = row['task_title'],
            description = row['task_description'],
            priority    = row['task_priority'],
            due_date    = row['due_date'],
            status      = row['task_status']
        )

    def update_task(self, task_id: str, user_id: str, title: str, description: str,
                    priority: str, due_date, status: str) -> None:
        
        """Update an existing task."""
        
        if priority not in self.VALID_PRIORITIES:
            priority = 'Normal'

        (
            self.client.table('tasks')
            .update({
                'task_title'       : title,
                'task_description' : description,
                'task_priority'    : priority,
                'due_date'    : str(due_date),
                'task_status'      : status
            })
            .eq('task_id', task_id)
            .eq('user_id', user_id)
            .execute()
        )

    def delete_task(self, task_id: str, user_id: str) -> None:
        """Delete a task."""
        (
            self.client.table('tasks')
            .delete()
            .eq('task_id', task_id)
            .eq('user_id', user_id)
            .execute()
        )

    def mark_overdue_tasks(self) -> None:

        """Mark all due tasks as OVERDUE."""
        today = dt.datetime.now(PK_TZ).date().isoformat()

        (
            self.client.table('tasks')
            .update({'task_status': 'OVERDUE'})
            .lt('due_date', today)
            .filter('task_status', 'not.in', '("COMPLETE","OVERDUE","✅️ COMPLETE")')
            .execute()
        )
    def get_future_tasks(self, user_id):
        '''This function is used to get tasks for
           day scheduling'''
        
        today = dt.date.today()
        future = (today + timedelta(days=11)).isoformat()

        response_task = (self.client.table('tasks').
                   select('task_id, task_title,task_priority,task_status,due_date').
                   eq('user_id', user_id).
                   gte('due_date', today.isoformat()).
                   lt('due_date', future).
                   filter('task_status', 'not.in', '("COMPLETE","OVERDUE","✅️ COMPLETE")').
                   execute()
                   )
        tasks = response_task.data

        if not tasks:
            return []
        
        task_ids = [task['task_id'] for task in tasks]

        response_subtask = (self.client.table('subtasks').
                                select('task_id','title','is_done').
                                in_('task_id',task_ids).
                                execute()
                            )
    
        subtasks_by_task = defaultdict(list)

        for item in response_subtask.data:
            subtasks_by_task[item['task_id']].append({
                "item": item['title'],
                "done": item['is_done']
            })

        # bundle each task with its subtasks and progress
        schedule_data = []
        for task in tasks:
            task_subtasks = subtasks_by_task[task['task_id']]
            total    = len(task_subtasks)
            done     = sum(1 for i in task_subtasks if i['done'])
            progress = int((done / total) * 100) if total > 0 else 0

            schedule_data.append({
                "title"         : task['task_title'],
                "priority"      : task['task_priority'],
                "status"        : task['task_status'],
                "due_date"      : task['due_date'],
                "days_until_due": (dt.datetime.strptime(task['due_date'], '%Y-%m-%d').date() - today).days,
                "progress"      : progress,
                "subtasks"      : task_subtasks
            })

        return schedule_data


class SubtaskManagement:

    """Handles all checklist operations against subtasks table."""

    def __init__(self, db = Database()):
        self.client = db.get_client()

    def add_subtask(self, task_id: str, title: str, user_id: str, is_done: bool = False) -> None:

        """Add a subtask to a given task_id."""

        self.client.table('subtasks').insert({
            'task_id'    : task_id,
            'title'      : title,
            'created_at' : dt.datetime.now().isoformat(),
            'is_done'    : is_done,
            'user_id'    : user_id
        }).execute()

    def toggle_subtask(self, item_id: str, is_done: bool) -> None:

        """Mark a subtask done or undone."""

        (
            self.client.table('subtasks')
            .update({'is_done': is_done})
            .eq('id', item_id)
            .execute()
        )
    
    def get_items(self, task_id: str) -> list:
        
        """Fetch all subtask items for a task (It is used in dashboard)."""

        response = (
            self.client.table('subtasks')
            .select('id, title, is_done')
            .eq('task_id', task_id)
            .execute()
        )

        return [
            Subtask_Item(
                item_id = row['id'],
                task_id = task_id,
                title   = row['title'],
                is_done = row['is_done']
            )
            for row in response.data
        ]

    def calc_progress(self, task_id: str) -> int:

        """Returns checklist completion % for a task."""

        response = (
            self.client.table('subtasks')
            .select('is_done')
            .eq('task_id', task_id)
            .execute()
        )

        if not response.data:
            return 0

        total = len(response.data)
        done  = sum(1 for row in response.data if row['is_done'])

        return int((done / total) * 100)
    

                



class Analytics:

    """Handles all dashboard queries."""

    def __init__(self, db =  Database()):
        self.client = db.get_client()

    def get_task_count(self, user_id: str) -> dict:
        """Returns count of tasks grouped by status."""
        response = (
            self.client.table('tasks')
            .select('task_status')
            .eq('user_id', user_id)
            .execute()
        )

        counts = {"total": len(response.data), "overdue": 0, "todo": 0, "in_progress": 0, "completed": 0}

        for row in response.data:
            s = row['task_status']
            if s == 'OVERDUE':
                counts["overdue"] += 1
            elif s in ('TO DO', '⚫ TO DO'):
                counts["todo"] += 1
            elif s in ('IN PROGRESS', '🔵 IN PROGRESS'):
                counts["in_progress"] += 1
            elif s in ('COMPLETE', '✅️ COMPLETE'):
                counts["completed"] += 1

        return counts

    def get_subtasks(self, user_id: str) -> list:

        """Returns unique task IDs that have subtasks."""

        response = (
            self.client.table('subtasks')
            .select('task_id')
            .eq('user_id', user_id)
            .execute()
        )

        seen = set()
        result = []

        for row in response.data:
            if row['task_id'] not in seen:
                seen.add(row['task_id'])
                result.append(row['task_id'])

        return result

    def get_monthly_progress(self, user_id: str) -> tuple:
        
        """Returns (total_tasks, percent_change, stats) for monthly analysis."""
        
        now = dt.datetime.now()

        current_start = dt.datetime(now.year, now.month, 1).date()
        current_end   = dt.datetime(now.year + (now.month // 12), (now.month % 12) + 1, 1).date()

        if now.month == 1:
            prev_start = dt.datetime(now.year - 1, 12, 1).date()
            prev_end   = dt.datetime(now.year, 1, 1).date()
        else:
            prev_start = dt.datetime(now.year, now.month - 1, 1).date()
            prev_end   = dt.datetime(now.year, now.month, 1).date()

        # fetch current month
        current = (
            self.client.table('tasks').select('task_status')
            .eq('user_id', user_id)
            .gte('due_date', current_start.isoformat())
            .lt('due_date', current_end.isoformat())
            .execute()
        )

        # fetch previous month
        previous = (
            self.client.table('tasks').select('task_status')
            .eq('user_id', user_id)
            .gte('due_date', prev_start.isoformat())
            .lt('due_date', prev_end.isoformat())
            .execute()
        )

        # count current month statuses in Python
        status_counts = {}
        for row in current.data:
            s = row['task_status']
            status_counts[s] = status_counts.get(s, 0) + 1

        total_tasks       = len(current.data)
        current_completed = status_counts.get('COMPLETE', 0) + status_counts.get('✅️ COMPLETE', 0)
        prev_completed    = sum(1 for row in previous.data if row['task_status'] in ('COMPLETE', '✅️ COMPLETE'))

        percent_change = 0
        if prev_completed > 0:
            percent_change = int(((current_completed - prev_completed) / prev_completed) * 100)

        stats = {
            "todo"      : round(((status_counts.get('TO DO', 0) + status_counts.get('⚫ TO DO', 0)) / total_tasks) * 100) if total_tasks else 0,
            "inprogress": round(((status_counts.get('IN PROGRESS', 0) + status_counts.get('🔵 IN PROGRESS', 0)) / total_tasks) * 100) if total_tasks else 0,
            "completed" : round((current_completed / total_tasks) * 100) if total_tasks else 0,
            "overdue"   : round((status_counts.get('OVERDUE', 0) / total_tasks) * 100) if total_tasks else 0
        }

        return total_tasks, percent_change, stats
