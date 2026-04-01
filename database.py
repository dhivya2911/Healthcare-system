import sqlite3
from werkzeug.security import generate_password_hash

DB_NAME = "healthcare.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # PATIENTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        disease TEXT,
        username TEXT
    )
    """)

    # DOCTORS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        specialization TEXT,
        username TEXT UNIQUE
    )
    """)

    # APPOINTMENTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        date TEXT
    )
    """)

    # ✅ CREATE DEFAULT ADMIN (ONLY IF NOT EXISTS)
    admin = cursor.execute(
        "SELECT * FROM users WHERE role='admin'"
    ).fetchone()

    if not admin:
        cursor.execute("""
            INSERT INTO users(username, password, role)
            VALUES (?, ?, ?)
            """, (
                "admin",
                generate_password_hash("admin123"),
                "admin"
            ))

    conn.commit()
    conn.close()