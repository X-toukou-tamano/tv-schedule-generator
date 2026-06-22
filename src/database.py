import sqlite3

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

    conn.commit()
    conn.close()

def save_records(records):
    if not records:
        return

    conn = get_connection()
    cursor = conn.cursor()

    # ① 更新対応：アップロードされたデータに含まれる日付の既存レコードを削除
    # （対象日のみ一旦リセットすることで、開催中止などによる「データの消失」も正確に反映する）
    unique_dates = list(set([str(record["date"]) for record in records]))
    
    # SQLiteでIN句を使うためのプレースホルダー(?, ?, ...)を動的に生成
    placeholders = ",".join(["?"] * len(unique_dates))
    
    cursor.execute(
        f"DELETE FROM calendar_events WHERE event_date IN ({placeholders})", 
        unique_dates
    )

    # ② 高速化：executemany で一括インサート
    data_to_insert = [(str(record["date"]), record["venue"]) for record in records]
    
    cursor.executemany(
        """
        INSERT INTO calendar_events (event_date, venue_name)
        VALUES (?, ?)
        """,
        data_to_insert
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
