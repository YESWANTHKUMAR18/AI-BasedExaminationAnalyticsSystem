# database.py
import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = "school_system.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Users table now includes subject
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT,
        subject TEXT
    )""")

    # Predictions table stays the same
    c.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        student_name TEXT,
        input_json TEXT,
        result TEXT,
        probability REAL,
        explanation TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()


def add_user(username, password, role="student", subject="General"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    password_hash = generate_password_hash(password)
    c.execute("""
        INSERT OR IGNORE INTO users (username, password_hash, role, subject)
        VALUES (?, ?, ?, ?)
    """, (username, password_hash, role, subject))
    conn.commit()
    conn.close()

def edit_user(username, new_role, new_subject, new_password=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if new_password:
        password_hash = generate_password_hash(new_password)
        c.execute("""
            UPDATE users SET role=?, subject=?, password_hash=? WHERE username=?
        """, (new_role, new_subject, password_hash, username))
    else:
        c.execute("""
            UPDATE users SET role=?, subject=? WHERE username=?
        """, (new_role, new_subject, username))
    conn.commit()
    conn.close()


def validate_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password_hash, role, subject FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    password_hash, role, subject = row
    if check_password_hash(password_hash, password):
        return {"role": role, "subject": subject}
    return None


def save_prediction(username, student_name, input_json, result, probability, explanation):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO predictions (username, student_name, input_json, result, probability, explanation)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, student_name, json.dumps(input_json), result, float(probability), explanation))
    conn.commit()
    conn.close()


def get_all_predictions():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, username, student_name, input_json, result, probability, explanation, timestamp
        FROM predictions
        ORDER BY timestamp DESC
    """)
    rows = c.fetchall()
    conn.close()
    columns = ['id','username','student_name','input_json','result','probability','explanation','timestamp']
    return [dict(zip(columns, r)) for r in rows]

def get_user_predictions(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, username, student_name, input_json, result, probability, explanation, timestamp
        FROM predictions
        WHERE username=?
        ORDER BY timestamp DESC
    """, (username,))
    rows = c.fetchall()
    conn.close()
    columns = ['id','username','student_name','input_json','result','probability','explanation','timestamp']
    return [dict(zip(columns, r)) for r in rows]
def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, role, subject FROM users")
    rows = c.fetchall()
    conn.close()
    return [{"username": r[0], "role": r[1], "subject": r[2]} for r in rows]

def delete_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()

def clear_predictions():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM predictions")
    conn.commit()
    conn.close()

def clear_non_admins():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE role != 'admin'")
    conn.commit()
    conn.close()

def setup_chat_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        role TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

def save_chat_message(username, role, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO chat_history (username, role, content)
        VALUES (?, ?, ?)
    """, (username, role, content))
    conn.commit()
    conn.close()

def get_chat_history(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT role, content
        FROM chat_history
        WHERE username=?
        ORDER BY id ASC
    """, (username,))
    rows = c.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in rows]

def clear_chat_history(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM chat_history WHERE username=?", (username,))
    conn.commit()
    conn.close()
