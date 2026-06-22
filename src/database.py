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
        venue_name TEXT NOT NULL,
        UNIQUE(event_date, venue_name)
    )
    """)

    conn.commit()

    conn.close()


def save_records(records):

    conn = get_connection()

    cursor = conn.cursor()

    for record in records:

        cursor.execute(
            """
            INSERT OR IGNORE INTO calendar_events
            (
                event_date,
                venue_name
            )
            VALUES (?, ?)
            """,
            (
                str(record["date"]),
                record["venue"]
            )
        )

    conn.commit()

    conn.close()


def get_events():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            event_date,
            venue_name
        FROM calendar_events
        ORDER BY event_date
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_summary():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            MIN(event_date),
            MAX(event_date),
            COUNT(*)
        FROM calendar_events
        """
    )

    row = cursor.fetchone()

    conn.close()

    return row
