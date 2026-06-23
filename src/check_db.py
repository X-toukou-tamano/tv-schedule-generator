import sqlite3
import os

db_path = "tv_schedule.db"
print(f"見に行くDBの場所: {os.path.abspath(db_path)}")

try:
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT event_date, venue_name FROM calendar_events ORDER BY event_date").fetchall()
    
    print(f"保存されているデータ件数: {len(rows)}件\n")
    
    if len(rows) > 0:
        print("【最初の10件を表示】")
        for row in rows[:10]:
            print(f"{row[0]} | {row[1]}")
    else:
        print("※データが0件です。アップロード時の保存処理が反映されていません。")

    conn.close()
except Exception as e:
    print(f"エラーが発生しました: {e}")
