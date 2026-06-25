import sqlite3
from zoneinfo import ZoneInfo

def get_connection():
    conn = sqlite3.connect("tv_schedule.db")
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_meta (
        meta_key TEXT PRIMARY KEY,
        meta_value TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_records(records):

    if not records:
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        unique_dates = list(
            set(
                [
                    str(record["date"])
                    for record in records
                ]
            )
        )

        placeholders = ",".join(
            ["?"] * len(unique_dates)
        )

        cursor.execute(
            f"""
            DELETE FROM calendar_events
            WHERE event_date IN ({placeholders})
            """,
            unique_dates
        )

        data_to_insert = [
            (
                str(record["date"]),
                record["venue"]
            )
            for record in records
        ]

        cursor.executemany(
            """
            INSERT OR IGNORE INTO
            calendar_events
            (
                event_date,
                venue_name
            )
            VALUES
            (
                ?,
                ?
            )
            """,
            data_to_insert
        )

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

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


def save_update_time():

    import datetime

    now_str = (
        datetime.datetime.now(
            ZoneInfo("Asia/Tokyo")
        )
        .strftime(
            "%Y/%m/%d %H:%M:%S"
        )
    )

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO
        system_meta
        (
            meta_key,
            meta_value
        )
        VALUES
        (
            'last_update',
            ?
        )
        """,
        (now_str,)
    )

    conn.commit()
    conn.close()


def get_update_time():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            meta_value
        FROM
            system_meta
        WHERE
            meta_key = 'last_update'
        """
    )

    row = cursor.fetchone()

    conn.close()

    return row[0] if row else None
