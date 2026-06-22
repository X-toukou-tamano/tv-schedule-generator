import sqlite3


def get_connection():

    conn = sqlite3.connect(
        "tv_schedule.db"
    )

    return conn


def create_tables():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_date TEXT NOT NULL,
        venue_name TEXT NOT NULL
    )
    """)

    conn.commit()

    conn.close()
