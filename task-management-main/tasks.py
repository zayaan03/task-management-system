import sqlite3
from auth import conn_db
import datetime as dt
import streamlit as st

##fetch tasks

def get_tasks(user_id):

    '''Collect all tasks of same user to show in CRUD'''
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT id, title, priority, due_date, status FROM tasks
           WHERE user_id = ?''',(user_id,)
    )
    tasks = cursor.fetchall()
    conn.close()
    return tasks

## add new task
def create_task(user_id, title, description, priority, due_date, status):

    conn = conn_db()
    cursor = conn.cursor()

    if not priority:
        priority = 'Normal'

    cursor.execute(
        '''INSERT INTO tasks (user_id,title,description,priority, due_date, status) 
            VALUES(?,?,?,?,?,?)''', (user_id,title,description,priority,due_date,status)
    )

    task_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return task_id


## get task for edit
def get_task_by_id(task_id, user_id):
    conn = conn_db()
    cursor = conn.cursor()

    cursor.execute(
        '''SELECT title, description, priority, due_date, status
            FROM tasks WHERE id=? AND user_id =?''', (task_id,user_id)
    )

    task = cursor.fetchone()
    conn.close()
    return task


## update task
def update_task(task_id, user_id, title, description, priority, due_date, status):

    '''Used in edit task to update new record'''
    conn = conn_db()
    cursor = conn.cursor()

    VALID_PRIORITIES = ("Low", "Normal", "High", "Urgent")
    if priority not in VALID_PRIORITIES:
        priority = "Normal"

    cursor.execute(
        '''UPDATE tasks 
           SET title=?, description=?, priority=?, due_date=?, status=?
           WHERE id=? AND user_id=?''',
        (title, description, priority, due_date, status, task_id, user_id)
    )

    conn.commit()
    conn.close()


## delete task
def delete_task(task_id, user_id):
    conn = conn_db()
    cursor = conn.cursor()

    cursor.execute(
        '''DELETE FROM tasks
            WHERE id=? AND user_id=?''', (task_id, user_id)
    )
    
    conn.commit()
    conn.close()


def mark_overdue_tasks():
    """
    Marks all tasks as OVERDUE where
    due date is more than today
    """

    today = dt.date.today().isoformat()

    conn = conn_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET status = 'OVERDUE'
        WHERE due_date < ?
        AND status NOT IN ('COMPLETE', 'OVERDUE', '✅️ COMPLETE')
    """, (today,))


    conn.commit()
    conn.close()


def add_checklist_item(task_id, title, user_id, is_done=False):
    """Creates checklist item in each task"""

    conn = conn_db()
    cursor = conn.cursor()

    cursor.execute(
        '''
        INSERT INTO task_checklist (task_id, title, created_at, is_done, user_id)
        VALUES (?,?,?,?,?)
        ''', (task_id, title, dt.datetime.now().isoformat(), int(is_done), user_id)
    )

    conn.commit()
    conn.close()

def add_edit_checklist_item():
    value = st.session_state.edit_checklist_input.strip()
    if value:
        st.session_state.edit_checklist.append({
            "id": None,          # None = new item
            "title": value,
            "checked": False
        })
        st.session_state.edit_checklist_input = ""


def done_checklist(item_id, is_done):
    conn = conn_db()
    cursor = conn.cursor()

    cursor.execute(
        '''
        UPDATE task_checklist
        SET is_done = ?
        WHERE id=?
        ''', (int(is_done), item_id)
    )

    conn.commit()
    conn.close()

def get_checklist(task_id):

    '''GET CHECKLIST ITEMS FOR EDIT'''
    conn = conn_db()
    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT id, title, is_done
        FROM task_checklist
        WHERE task_id = ?
        ''', (task_id,)
    )

    items = cursor.fetchall()
    conn.close()

    return items

def add_draft_checklist_item():
    text = st.session_state.checklist_input.strip()

    if not text:
        return

    st.session_state.draft_checklist.append({
        "title": text,
        "checked": False
    })

    # clear input
    st.session_state.checklist_input = ""



## ==============================================

## These are the functions used in dashboard page

## ==============================================

def get_checklist_tasks(user_id):
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT DISTINCT task_id FROM task_checklist
           WHERE user_id=?''', (user_id,)
    )
    task_ids = cursor.fetchall()
    conn.close()
    return task_ids

def get_task_count(user_id):
    overdue = 0
    todo = 0
    in_progress = 0
    completed = 0
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT status FROM tasks
           WHERE user_id = ?''',(user_id,)
    )

    task_count= cursor.fetchall()
    conn.close()

    for i in task_count:
        if i[0] == 'OVERDUE':
            overdue += 1
        elif i[0] == 'TO DO' or i[0] == "⚫ TO DO":
            todo += 1
        elif i[0] == 'IN PROGRESS' or i[0] == '🔵 IN PROGRESS':
            in_progress += 1
        elif i[0] == '✅️ COMPLETE' or i[0] == 'COMPLETE':
            completed += 1

    return {
        "total": len(task_count),
        "overdue": overdue,
        "todo": todo,
        "in_progress": in_progress,
        "completed": completed
    }



def calc_task_progress(task_id):
    ''''Calculate task progress according to checklist'''

    conn = conn_db()
    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT COUNT(*), SUM(is_done)
        FROM task_checklist
        WHERE task_id = ?
        ''', (task_id, )
    )
    
    result = cursor.fetchone()
    conn.close()

    if result is None or result[0] == 0:
        return 0
    
    total, done = result
    return int((done or 0) / total * 100)


def get_monthly_progress(user_id):


    now = dt.datetime.now()
    current_start = dt.datetime(now.year, now.month, 1).date()
    current_end = dt.datetime(now.year + (now.month // 12), (now.month % 12) + 1, 1).date()

    # Previous month
    if now.month == 1:
        prev_start = dt.datetime(now.year - 1, 12, 1).date()
        prev_end = dt.datetime(now.year, 1, 1).date()
    else:
        prev_start = dt.datetime(now.year, now.month - 1, 1).date()
        prev_end = dt.datetime(now.year, now.month, 1).date()

    conn = conn_db()
    cursor = conn.cursor()

    # query for current month progress
    cursor.execute('''
        SELECT status, COUNT(*) FROM tasks
        WHERE user_id = ? AND due_date >= ? AND due_date < ?
        GROUP BY status
    ''', (user_id, current_start.isoformat(), current_end.isoformat()))
    current_status_counts = dict(cursor.fetchall())

    total_tasks = sum(current_status_counts.values())
    current_completed = current_status_counts.get('COMPLETE', 0) + current_status_counts.get('✅️ COMPLETE', 0)

    # query for previous month progress
    cursor.execute('''
        SELECT COUNT(*) FROM tasks
        WHERE user_id = ? AND due_date >= ? AND due_date < ? AND (status = 'COMPLETE' OR status = '✅️ COMPLETE')
    ''', (user_id, prev_start.isoformat(), prev_end.isoformat()))
    prev_completed_result = cursor.fetchone()
    prev_completed = prev_completed_result[0] if prev_completed_result else 0

    conn.close()

    # percent change
    if prev_completed > 0:
        percent_change = int(((current_completed - prev_completed) / prev_completed) * 100)
    else:
        percent_change = 0  # Or handle as "N/A" if preferred

    # stats with counts for current month
    stats = {
        "todo": round(((current_status_counts.get('TO DO', 0) + current_status_counts.get('⚫ TO DO', 0))/total_tasks)*100) if total_tasks > 0 else 0,
        "inprogress": round(((current_status_counts.get('IN PROGRESS', 0) + current_status_counts.get('🔵 IN PROGRESS', 0))/total_tasks)*100) if total_tasks > 0 else 0,
        "completed": round((current_completed/total_tasks) * 100),
        "overdue": round((current_status_counts.get('OVERDUE', 0) / total_tasks) *100) if total_tasks > 0 else 0
    }

    return total_tasks, percent_change, stats






