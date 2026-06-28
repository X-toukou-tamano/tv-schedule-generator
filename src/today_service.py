from datetime import date

from database import get_events
from event_sorter import split_and_sort_events
from keirin_schedule import get_schedule


def get_today_sorted_data():
    """
    スケジュールデータ構築（公開判定によるbreak付き）
    """

    rows = get_events()

    excel_data = []

    for event_date, venue_name in rows:

        excel_data.append(
            {
                "date": date.fromisoformat(event_date),
                "venue": venue_name,
            }
        )

    months = sorted({
        (row["date"].year, row["date"].month)
        for row in excel_data
    })

    return schedule_data_by_date

    vinfo_map = {}

    for info in race_data["RaceList"]:

        key = (
            info["kaisaiDate"],
            info["keirinjoName"]
        )

        vinfo_map[key] = info

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

            key = (
                event_date.replace("-", ""),
                venue_name
            )

            # 1場でも欠けたら終了
            if key not in vinfo_map:
                is_all_venues_available = False
                break

            info = vinfo_map[key]

            kubun_code = str(
                info.get(
                    "kubunIconName",
                    ""
                )
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
                    "grade": info.get(
                        "gradeIconName",
                        "-"
                    ),
                    "status": info.get(
                        "nichijiIconName",
                        "-"
                    ),
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
