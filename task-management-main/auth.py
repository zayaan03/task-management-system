import sqlite3
import hashlib

##encrypting password
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()


##db connection
def conn_db():
    conn = sqlite3.connect('task-management.db')
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn

##signup block
def register_user(username, email, password):
    conn = conn_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
        """, (username, email, hash_pass(password)))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()

##login block
def login_user(username, password):
    conn = conn_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, email
        FROM users
        WHERE username = ? AND password = ?
    """, (username, hash_pass(password)))

    user = cursor.fetchone()
    conn.close()

    return user
