import datetime as dt
import time
from auth import conn_db
import smtplib
from email.message import EmailMessage
import os


EMAILS_PER_MIN = 5
DELAY_SECONDS = 60 // EMAILS_PER_MIN   


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

def run_email_scheduler():
    slot = get_current_slot()
    if not slot:
        return

    today = dt.date.today().isoformat()
    slot_key = f"{today}_{slot}"

    users = get_all_users()  # id, email

    sent_count = 0

    for user_id, email in users:

        if email_already_sent(user_id, slot_key):
            continue

        tasks = get_due_tasks(user_id)

        if not tasks:
            continue

        body = build_email_body(tasks)
        send_email(email, "Task Reminder", body)

        log_email_sent(4, slot_key)
        sent_count += 1

        if sent_count % EMAILS_PER_MIN == 0:
            time.sleep(60)
        else:
            time.sleep(DELAY_SECONDS)

def get_due_tasks(user_id):
    today = dt.date.today().isoformat()
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute("""
            SELECT title, due_date, status
            FROM tasks
            WHERE user_id = ?
            AND status != 'COMPLETE'
            AND due_date == ?
            """,(user_id, today))
    rows = cursor.fetchall()
    conn.close()
    return rows



def email_already_sent(user_id, slot_key):
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM email_log WHERE user_id=? AND slot_key=?",
        (user_id, slot_key)
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def log_email_sent(user_id, slot_key):
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO email_log (user_id, slot_key, created_at) VALUES (?, ?, ?)",
        (user_id, slot_key, dt.datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def handle_new_task(task):
    now = dt.datetime.now()
    today = dt.date.today()

    if now.hour >= 9 and task.due_date == today:
        time.sleep(10)   # short delay
        send_email(task)
        
def email_already_sent(user_id, slot_key):
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM email_log WHERE user_id=? AND slot_key=?",
        (user_id, slot_key)
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def log_email_sent(user_id, slot_key):
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO email_log (user_id, slot_key, created_at) VALUES (?, ?, ?)",
        (user_id, slot_key, dt.datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
def get_all_users():
    """
    Fetch all users (id, email) from the DB.
    Returns a list of tuples: [(id1, email1), (id2, email2), ...]
    """
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email FROM users")
    users = cursor.fetchall()
    conn.close()
    return users


# ---------- CONFIG ----------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("APP_PASSWORD")  
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
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Error sending email to {to_email}: {e}")
    
if __name__ == "__main__":
    run_email_scheduler()




