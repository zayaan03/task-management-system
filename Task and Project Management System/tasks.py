import sqlite3
from auth import conn_db

##fetch tasks

def get_tasks(user_id):
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT id, title, priority, due_date, status FROM tasks
        WHERE user_id = ?''',(user_id)
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

    conn.commit()
    conn.close()


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

## check task overdue
def check_overdue(user_id):
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT title, FROM tasks
           WHERE user_id=?''', (user_id)
    )
