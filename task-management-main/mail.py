import datetime as dt
import time
from auth import conn_db
from database import init_db
import smtplib
from email.message import EmailMessage
import os
import pytz
import streamlit as st

PK_TZ = pytz.timezone("Asia/Karachi")
now = dt.datetime.now(PK_TZ)
today = now.date()

EMAILS_PER_MIN = 5
DELAY_SECONDS = 60 // EMAILS_PER_MIN   


def get_all_users():
    """
    Fetch all users (id, email) from the db
    """
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email FROM users")
    users = cursor.fetchall()
    conn.close()
    return users


def get_due_tasks(user_id):
    now = dt.datetime.now(PK_TZ)
    today = now.date().isoformat()   
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, due_date, status
        FROM tasks
        WHERE user_id = ?
          AND due_date = ?
          AND status NOT IN ('✅️ COMPLETE', 'COMPLETE')
    """, (user_id, today))
    
    rows = cursor.fetchall()
    conn.close()
    return rows
    
def get_current_slot():
    # now = dt.datetime.now()
    # if now.hour == 9 and now.minute <= 5:
    #     return "morning"
    # if now.hour == 17 and now.minute <= 5:
    #     return "evening"
    return 'test'

def build_email_body(tasks):
    lines = ["Here are your task reminders:\n"]

    for t in tasks:
        title, due_date, status = t
        lines.append(f"- {title} | Due: {due_date} | Status: {status}")

    lines.append("\nStay organized.")
    return "\n".join(lines)

        
# def email_already_sent(user_id, slot_key):
#     conn = conn_db()
#     cursor = conn.cursor()
#     cursor.execute(
#         "SELECT 1 FROM email_log WHERE user_id=? AND slot_key=?",
#         (user_id, slot_key)
#     )
#     exists = cursor.fetchone() is not None
#     conn.close()
#     return exists

# def log_email_sent(user_id, slot_key):
#     conn = conn_db()
#     cursor = conn.cursor()
#     cursor.execute(
#         "INSERT INTO email_log (user_id, slot_key, created_at) VALUES (?, ?, ?)",
#         (user_id, slot_key, dt.datetime.now().isoformat())
#     )
#     conn.commit()
#     conn.close()


# ---------- CONFIG ----------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "zayaanscherg06@gmail.com"
EMAIL_PASSWORD = "edcx ajpq sodf cuhk"  
# ----------------------------

def send_email(to_email, subject, body):
    """
    Send a simple plain-text email using SMTP
    """
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()  # secure connection
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            st.success('email sent success')
    except Exception as e:
        st.error('unable to send email')
    
def run_email_scheduler():
    slot = get_current_slot()
    if not slot:
        return

    now = dt.datetime.now(PK_TZ)
    today = now.date()
    slot_key = f"{today}_{slot}"
    users = get_all_users()  # id, email
    st.write(users)
    sent_count = 0

    for user_id, email in users:

        # if email_already_sent(user_id, slot_key):
        #     st.write('email already sent')
        #     continue
        userid = int(user_id)
        tasks = get_due_tasks(userid)
        st.write('task',tasks)
        if not tasks:
            st.write('tasks not found')
            continue

        body = build_email_body(tasks)
        send_email(email, "Task Reminder", body)
        st.write('email sent')
        # log_email_sent(user_id, slot_key)
        sent_count += 1

        if sent_count % EMAILS_PER_MIN == 0:
            time.sleep(60)
        else:
            time.sleep(DELAY_SECONDS)
    









































