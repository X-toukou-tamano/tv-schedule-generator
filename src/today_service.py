from datetime import date

from database import get_events
from event_sorter import split_and_sort_events

def get_today_sorted_data():
    """
    スケジュールデータ構築（公開判定によるbreak付き）
    """

    rows = get_events()

    excel_data = []

    for (
        event_date,
        venue_name,
        grade,
        kubun,
        nichiji,
    ) in rows:

        excel_data.append(
            {
                "date": date.fromisoformat(event_date),
                "venue": venue_name,
                "grade": grade,
                "kubun": kubun,
                "nichiji": nichiji,
            }
        )

    # 1. まずExcelデータを日付ごとにまとめる
    excel_by_date = {}

    for row in excel_data:

        event_date = row["date"].isoformat()

        if event_date not in excel_by_date:
            excel_by_date[event_date] = []

        excel_by_date[event_date].append(row)

    # 最終的な結果を格納する辞書
    schedule_data_by_date = {}

    # 2. 日付ごとに1日ずつ処理
    for event_date in sorted(excel_by_date.keys()):

        # その日の全場が揃っているかチェック
        is_all_venues_available = True
        current_day_merged_data = []

        for row in excel_by_date[event_date]:

            venue_name = row["venue"]

            grade = row["grade"]
            kubun = row["kubun"]
            nichiji = row["nichiji"]

            if not grade or not kubun or not nichiji:
                is_all_venues_available = False
                break

            kubun_code = str(
                kubun
            ).strip()

            if kubun_code == "1":
                session_type = "day"

            elif kubun_code == "3":
                session_type = "night"

            else:
                continue

            current_day_merged_data.append(
                {
                    "name": venue_name,
                    "session": session_type,
                    "grade": grade,
                    "status": nichiji,
                }
            )

        # 1場でも未公開ならそこで終了
        if not is_all_venues_available:
            break

        day_events, night_events = split_and_sort_events(
            current_day_merged_data
        )

        preview_day = [
            {
                "name": ev["name"],
                "grade": ev["grade"],
                "status": ev["status"],
            }
            for ev in day_events
        ]

        preview_night = [
            {
                "name": ev["name"],
                "grade": ev["grade"],
                "status": ev["status"],
            }
            for ev in night_events
        ]

        schedule_data_by_date[event_date] = (
            day_events,
            night_events,
            preview_day,
            preview_night,
        )

    return schedule_data_by_date
