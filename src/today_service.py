from event_sorter import split_and_sort_events
from excel_reader import parse_excel
from keirin_schedule import get_schedule


def get_today_sorted_data():
    """
    スケジュールデータ構築（公開判定によるbreak付き）
    """

    excel_data = parse_excel()

    months = sorted({
        (row["date"].year, row["date"].month)
        for row in excel_data
    })

    race_data = get_schedule(months)

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

            # 1場でも欠けたらフラグを倒してループを抜ける
            if key not in vinfo_map:
                is_all_venues_available = False
                break

            # 存在する場合はデータを抽出
            info = vinfo_map[key]

            kubun_code = str(
                info.get(
                    "kubunIconName",
                    ""
                )
            ).strip()

            session_type = None

            if kubun_code == "1":
                session_type = "day"

            elif kubun_code == "3":
                session_type = "night"

            else:
                continue

            status_text = info.get(
                "nichijiIconName",
                "-"
            )

            grade_text = info.get(
                "gradeIconName",
                "-"
            )

            current_day_merged_data.append(
                {
                    "name": venue_name,
                    "session": session_type,
                    "grade": grade_text,
                    "status": status_text,
                }
            )

        # 1場でも欠けていたら、翌日以降の処理もすべて終了（break）
        if not is_all_venues_available:
            break

        # 全部揃っていれば分類・ソートを行う
        day_events, night_events = split_and_sort_events(
            current_day_merged_data
        )

        preview_day = []

        for ev in day_events:

            preview_day.append(
                {
                    "name": ev["name"],
                    "grade": ev["grade"],
                    "status": ev["status"],
                }
            )

        preview_night = []

        for ev in night_events:

            preview_night.append(
                {
                    "name": ev["name"],
                    "grade": ev["grade"],
                    "status": ev["status"],
                }
            )

        # 結果を格納
        schedule_data_by_date[event_date] = (
            day_events,
            night_events,
            preview_day,
            preview_night,
        )

    return schedule_data_by_date
