import google.genai as genai
import os
from dotenv import load_dotenv
from tasks import TaskManagement, SubtaskManagement
import datetime as dt
import json
from datetime import timedelta

load_dotenv()
 

class AIFeatures():

    def __init__(self):
        self.client = genai.Client(api_key = st.secrets['GEMINI_API_KEY'])
        self.model = 'gemini-2.0-flash'
    
    def get_task_breakdown(self, task_title: str):

        self.task_title = task_title

        TASK_BREAKDOWN_PROMPT = f"""
                You are a productivity assistant inside a task management app.

                When a user gives you a task title, analyze 
                it and respond in one of two ways:

                ## For SIMPLE tasks (single action, straightforward):
                Return only a 1-2 sentence description of what the task involves.

                ## For COMPLEX tasks (projects, builds, multi-step work):
                Return a short 1-2 sentence description followed by a breakdown of 4-6 clear milestones.

                ## Rules:
                - Simple tasks: writing emails, fixing bugs, making calls, reading, basic edits
                - Complex tasks: building apps, designing systems, creating content, launching products
                - Milestones should be action-oriented and specific to the task given
                - Keep description under 40 words
                - Keep each milestone under 10 words
                - Do not add any extra explanation, greetings or commentary

                ## Output format for simple tasks:
                DESCRIPTION: <your description here>

                ## Output format for complex tasks:
                DESCRIPTION: <your description here>
                MILESTONES:
                1. <milestone 1>
                2. <milestone 2>
                3. <milestone 3>
                4. <milestone 4>
                5. <milestone 5>

                Task title: {self.task_title}
                """ 
        response = self.client.models.generate_content(
        model = self.model,
        contents = TASK_BREAKDOWN_PROMPT
        )
        return response.text
    
    def nl_task_creation(self, user_input: str, user_id: str, conversation_history: list = None) -> dict:
        """
        Takes natural language input, extracts task data,
        saves to database using create_task and add_item.
        Returns dict with status and message for UI.
        """

        if conversation_history is None:
            conversation_history = []

        today = dt.date.today()

        SYSTEM_PROMPT = f"""
                You are a task creation assistant inside a productivity management app.
                Today's date is {today.strftime("%A, %B %d, %Y")}.

                Your job is to extract task information from the user's natural language input
                and return structured JSON data.

                ## TASK COMPLEXITY DETECTION:
                - SIMPLE task: single action, done in one sitting (submit assignment, reply email, fix bug, make call)
                - COMPLEX task: multi-step project requiring planning (build website, design system, create app, launch product)

                ## WHAT TO EXTRACT:
                - title: clear concise task title
                - description: 
                - Simple task: 1 sentence description
                - Complex task: 2-3 sentence helpful guidance description
                - priority: detect from keywords
                - "urgent", "asap", "critical", "today" → Urgent
                - "important", "soon", "high" → High  
                - default → Normal
                - "low", "whenever", "someday" → Low
                - due_date: convert to YYYY-MM-DD format
                - "today" → {today.isoformat()}
                - "tomorrow" → {(today + timedelta(days=1)).isoformat()}
                - "next friday" → calculate actual date
                - "in 3 days" → calculate actual date
                - if no date mentioned → null
                - status: detect from context
                - "working on", "started", "in progress" → IN PROGRESS
                - default → TO DO
                - is_complex: true or false
                - checklist: 
                - Simple task: empty list []
                - Complex task: 4-6 specific actionable subtasks

                ## PRIORITY OPTIONS (use exactly these values):
                - "urgent", "asap", "critical", "today" → Urgent
                - "important", "soon", "high"           → High
                - default                               → Normal
                - "low", "whenever", "someday"          → Low

                Valid priority values: Low, Normal, High, Urgent

                ## STATUS OPTIONS (use exactly these values with icons):
                - "working on", "started", "currently", "in progress" → 🔵 IN PROGRESS
                - "done", "finished", "completed", "already done"     → ✅️ COMPLETE
                - default                                              → ⚫ TO DO

                Valid status values: ⚫ TO DO, 🔵 IN PROGRESS, ✅️ COMPLETE

                ## RESPONSE RULES:
                - If you have enough information → return status "ready" with full task data
                - If missing critical info (no title unclear request) → return status "needs_info" with a specific question
                - Never ask more than one question at a time
                - If due date is missing, still return "ready" with due_date as null
                - Always return valid JSON only, no extra text, no markdown backticks

                ## JSON FORMAT:

                If needs more info:
                {{
                    "status": "needs_info",
                    "question": "your specific question here"
                }}

                If ready to save:
                {{
                    "status": "ready",
                    "task": {{
                        "title": "task title here",
                        "description": "task description here",
                        "priority": "Normal",
                        "due_date": "2026-06-25",
                        "status": "TO DO",
                        "is_complex": false,
                        "checklist": []
                    }},
                    "summary": "Here is what I will create: [brief human readable summary]"
                }}
                """

        # build conversation for multi turn
        messages = f"{SYSTEM_PROMPT}\n\n"
        
        for msg in conversation_history:
            role  = msg['role']
            text  = msg['text']
            messages += f"{role.upper()}: {text}\n"
        
        messages += f"USER: {user_input}"

        response = self.client.models.generate_content(
            model=self.model,
            contents=messages
        )

        raw = response.text.strip()

        # strip markdown backticks if gemini adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            return {
                "status"  : "error",
                "message" : "AI returned invalid response. Please try again."
            }

        # if ready — save to database
        if result.get("status") == "ready":
            task  = result["task"]

            # create the task using existing method
            task_id = TaskManagement().create_task(
                user_id     = user_id,
                title       = task["title"],
                description = task["description"],
                priority    = task["priority"],
                due_date    = task["due_date"],
                status      = task["status"]
            )

            # add checklist items if complex task
            if task["is_complex"] and task["checklist"] and task_id:
                for item in task["checklist"]:
                    SubtaskManagement().add_subtask(
                        task_id  = task_id,
                        title    = item,
                        user_id  = user_id,
                        is_done  = False
                    )

            return {
                "status"  : "saved",
                "summary" : result["summary"],
                "task_id" : task_id
            }

        # if needs more info — return question to show user
        if result.get("status") == "needs_info":
            return {
                "status"  : "needs_info",
                "question": result["question"]
            }

        return {
            "status"  : "error",
            "message" : "Something went wrong. Please try again."
        }

        
    def generate_daily_schedule(self, user_id: str, user_name: str):

        schedule_data = TaskManagement().get_future_tasks(user_id)

        if not schedule_data:
            return "No upcoming tasks found for scheduling."
        
        today     = dt.date.today()
        day_name  = today.strftime("%A")
        date_str  = today.strftime("%B %d, %Y")

        tasks_context = ""
        for i, task in enumerate(schedule_data, 1):
            tasks_context += f"""
                Task {i}:
                - Title: {task['title']}
                - Priority: {task['priority']}
                - Status: {task['status']}
                - Due Date: {task['due_date']} ({task['days_until_due']} days left)
                - Progress: {task['progress']}%
                - Subtasks:"""
        
        if task['subtasks']:
            for subtask in task['subtasks']:
                status = "✅" if subtask['done'] else "⬜"
                tasks_context += f"\n  {status} {subtask['item']}"
        else:
            tasks_context += "\n  No subtasks defined"
        
        tasks_context += "\n"

        SCHEDULE_PROMPT = f"""
            You are an elite personal productivity coach and scheduling expert 
            inside an AI-powered task management app.

            Today is {day_name}, {date_str}.
            You are creating a personalized daily schedule for {user_name}.
            Working hours are 9:00 AM to 6:00 PM (Asia/Karachi timezone).

            ## YOUR GOAL:
            Create a smart, realistic and personalized daily schedule that maximizes 
            {user_name}'s productivity today while keeping future deadlines in mind.

            ## TASKS TO SCHEDULE:
            {tasks_context}

            ## SCHEDULING RULES:

            ### Priority & Difficulty:
            - Schedule URGENT and HIGH priority tasks in morning (9AM-12PM) — peak focus hours
            - Schedule NORMAL priority tasks in afternoon (12PM-4PM)
            - Schedule LOW priority tasks in late afternoon (4PM-6PM)
            - Harder and more complex tasks always get morning slots
            - If a task has many incomplete subtasks and is due soon — give it maximum time today

            ### Time Allocation:
            - Simple tasks with no subtasks: 30-60 minutes
            - Medium complexity tasks: 1-2 hours
            - Complex tasks (many subtasks, big projects): 2-3 hours max per block
            - Never schedule one task for more than 3 hours in a single block
            - If a complex task needs more time, split it into two blocks with a break between

            ### Subtask Awareness:
            - If a task is 80%+ complete — only schedule remaining subtasks, keep it short
            - If a task is 0% complete and due within 2 days — mark it as CRITICAL and prioritize it
            - Only assign incomplete subtasks to today — skip completed ones
            - If a task has no subtasks but is complex (building apps, designing systems) — 
            warn {user_name} to break it down first, but still schedule 1 hour to make a start

            ### Future Task Awareness:
            - If a task is due tomorrow but {user_name} has lighter tasks today — 
            give extra time to that tomorrow task today
            - If a task is due in 7-10 days but is highly complex — 
            schedule at least 1 hour today to make early progress

            ### Breaks:
            - Add a 15 minute break after every heavy/complex task block
            - Add a 1 hour lunch break between 1PM-2PM always
            - If {user_name} has 3+ consecutive heavy tasks — add an extra 10 minute breather

            ### Day Assessment:
            - Look at the full picture of tasks — is today a heavy day or light day?
            - If light day and heavy tasks tomorrow — redistribute some work to today
            - If heavy day — be realistic, dont overload the schedule

            ## OUTPUT FORMAT:
            Follow this exact format — no deviations:

            GREETING:
            <Write a warm 2-3 sentence personalized greeting addressing {user_name} by name. 
            Comment on what kind of day today looks like based on their tasks. 
            Be encouraging but realistic.>

            DAY OVERVIEW:
            <1-2 sentences summarizing today's focus and most critical priority>

            SCHEDULE:
            <time> - <time> → <specific action or subtask> (<task title>) [<PRIORITY LEVEL>]

            WARNINGS:
            <Only include if there are real concerns. Each warning on new line starting with ⚠️>
            ⚠️ <warning 1>
            ⚠️ <warning 2>

            SCHEDULE SCORE: <X>/10
            SCORE REASON: <One sentence explaining the score>

            ## IMPORTANT RULES FOR OUTPUT:
            - Be specific — dont say "work on task", say exactly which subtask to do
            - Use {user_name}'s name at least once in the greeting
            - Warnings only for real issues — tasks at risk, unrealistic deadlines, no subtasks on complex work
            - Keep the schedule tight and realistic — dont schedule more than 8 hours of work in 9 hours
            - If no warnings needed write: WARNINGS: None
            - Always include lunch break at 1PM
            """

        response = self.client.models.generate_content(
        model=self.model,
        contents=SCHEDULE_PROMPT)

        return response.text
