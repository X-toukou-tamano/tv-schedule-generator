import sqlite3
import os

def get_connection():

    db_path = "tv_schedule.db"

    print(
        f"DB PATH = {os.path.abspath(db_path)}"
    )

    conn = sqlite3.connect(
        db_path
    )

    return conn

def create_tables():

    print("★★★★ create_tables 開始 ★★★★")

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

    print("★★★★ create_tables 終了 ★★★★")

def save_records(records):
    print(f"\n--- [DB LOG] save_records 開始 ---")
    print(f"[DB LOG] 受け取ったデータ件数: {len(records)}件")
    
    if not records:
        print("[DB LOG] 保存するデータがありません。終了します。")
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        unique_dates = list(set([str(record["date"]) for record in records]))
        placeholders = ",".join(["?"] * len(unique_dates))
        
        print(f"[DB LOG] 既存データの削除開始 (対象日付: {len(unique_dates)}日分)...")
        cursor.execute(
            f"DELETE FROM calendar_events WHERE event_date IN ({placeholders})", 
            unique_dates
        )
        print(f"[DB LOG] 削除完了: {cursor.rowcount}件の古いデータを消去しました")

        data_to_insert = [(str(record["date"]), record["venue"]) for record in records]
        
        print(f"[DB LOG] 新規データのINSERT開始...")
        # 重複エラー(UNIQUE制約)で落ちないように INSERT OR IGNORE に変更
        cursor.executemany(
            """
            INSERT OR IGNORE INTO calendar_events (event_date, venue_name)
            VALUES (?, ?)
            """,
            data_to_insert
        )
        print(f"[DB LOG] INSERT完了: {cursor.rowcount}件のデータを追加しました")

        conn.commit()
        print("[DB LOG] コミット成功！DBに確実に書き込みました。")

    except Exception as e:
        print(f"[DB LOG] ❌ エラー発生: {e}")
        conn.rollback()

    finally:
        conn.close()
        print("--- [DB LOG] save_records 終了 ---\n")

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
    # 「2026/06/23 15:30:45」のような形式で現在日時を取得
    now_str = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO system_meta (meta_key, meta_value)
        VALUES ('last_update', ?)
    """, (now_str,))
    conn.commit()
    conn.close()

# 【追加】アップデート日時を取得する関数
def get_update_time():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT meta_value FROM system_meta WHERE meta_key = 'last_update'")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None
