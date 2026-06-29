raise Exception("DATABASE.PY 読み込まれた")

import sqlite3
import datetime
from zoneinfo import ZoneInfo

import os

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "tv_schedule.db"
)

def get_connection():
    return sqlite3.connect("tv_schedule.db")


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_date TEXT NOT NULL,
        venue_name TEXT NOT NULL,
        grade TEXT,
        kubun TEXT,
        nichiji TEXT,
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

    cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    """)

    tables = cursor.fetchall()

    for column in ("grade", "kubun", "nichiji"):
        try:
            cursor.execute(
                f"ALTER TABLE calendar_events ADD COLUMN {column} TEXT"
            )
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()

    return tables

def save_records(records):

    if not records:
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_date TEXT NOT NULL,
            venue_name TEXT NOT NULL,
            grade TEXT,
            kubun TEXT,
            nichiji TEXT,
            UNIQUE(event_date, venue_name)
        )
        """)

        unique_dates = sorted(
            {
                str(record["date"])
                for record in records
            }
        )

        cursor.executemany(
            """
            DELETE FROM calendar_events
            WHERE event_date = ?
            """,
            [(d,) for d in unique_dates]
        )

        cursor.executemany(
            """
            INSERT OR REPLACE INTO calendar_events
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
            [
                (
                    str(record["date"]),
                    record["venue"],
                )
                for record in records
            ]
        )

        conn.commit()

        cursor.execute(
            "SELECT COUNT(*) FROM calendar_events"
        )
        return cursor.fetchone()[0]

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()

def update_event_info(records):
    """
    records = [
        {
            "date": "2026-04-01",
            "venue": "京王閣",
            "grade": "F1",
            "kubun": "3",
            "nichiji": "初日"
        },
        ...
    ]
    """

    if not records:
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.executemany(
            """
            UPDATE calendar_events
            SET
                grade = ?,
                kubun = ?,
                nichiji = ?
            WHERE
                event_date = ?
            AND
                venue_name = ?
            """,
            [
                (
                    r["grade"],
                    r["kubun"],
                    r["nichiji"],
                    str(r["date"]),
                    r["venue"]
                )
                for r in records
            ]
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
            venue_name,
            grade,
            kubun,
            nichiji
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

    raise Exception(row)

def save_update_time():

    now_str = (
        datetime.datetime.now(
            ZoneInfo("Asia/Tokyo")
        )
        .strftime("%Y/%m/%d %H:%M:%S")
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


def save_generate_history(
    history_type,
    start_date,
    end_date,
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO system_meta
        (
            meta_key,
            meta_value
        )
        VALUES
        (
            ?,
            ?
        )
        """,
        (
            f"{history_type}_from",
            str(start_date),
        ),
    )

    cursor.execute(
        """
        INSERT OR REPLACE INTO system_meta
        (
            meta_key,
            meta_value
        )
        VALUES
        (
            ?,
            ?
        )
        """,
        (
            f"{history_type}_to",
            str(end_date),
        ),
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


def get_generate_history(
    history_type,
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT meta_value
        FROM system_meta
        WHERE meta_key = ?
        """,
        (
            f"{history_type}_from",
        ),
    )

    row_from = cursor.fetchone()

    cursor.execute(
        """
        SELECT meta_value
        FROM system_meta
        WHERE meta_key = ?
        """,
        (
            f"{history_type}_to",
        ),
    )

    row_to = cursor.fetchone()

    conn.close()

    return (
        row_from[0] if row_from else None,
        row_to[0] if row_to else None,
    )
