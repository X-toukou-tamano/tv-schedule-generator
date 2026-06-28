from datetime import date

from database import get_events
from event_sorter import split_and_sort_events


def get_schedule_data(start_date, end_date):
    """
    指定期間のスケジュールデータ構築
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

        event_date_obj = date.fromisoformat(
            event_date
        )

        if not (
            start_date
            <= event_date_obj
            <= end_date
        ):
            continue

        excel_data.append(
            {
                "date": event_date_obj,
                "venue": venue_name,
                "grade": grade,
                "kubun": kubun,
                "nichiji": nichiji,
            }
        )

    excel_by_date = {}

    for row in excel_data:

        event_date = row["date"].isoformat()

        if event_date not in excel_by_date:
            excel_by_date[event_date] = []

        excel_by_date[event_date].append(
            row
        )

    schedule_data_by_date = {}

    for event_date in sorted(
        excel_by_date.keys()
    ):

        is_all_venues_available = True

        current_day_merged_data = []

        for row in excel_by_date[event_date]:

            venue_name = row["venue"]
            grade = row["grade"]
            kubun = row["kubun"]
            nichiji = row["nichiji"]

            if (
                not grade
                or not kubun
                or not nichiji
            ):
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
