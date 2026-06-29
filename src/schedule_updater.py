from collections import defaultdict
from datetime import datetime

from database import (
    get_events,
    update_event_info,
)

from keirin_schedule import (
    get_schedule,
)


def update_schedule_info():
    """
    DB(date, venue)に
    grade / kubun / nichiji
    を付与する。
    """

    events = get_events()

    if not events:
        return 0

    # -----------------------------
    # 対象月抽出
    # -----------------------------
    months = set()

    for row in events:

        event_date = row[0]

        d = datetime.strptime(
            event_date,
            "%Y-%m-%d"
        )

        months.add(
            (
                d.year,
                d.month,
            )
        )

    # -----------------------------
    # KEIRIN.JP取得
    # -----------------------------
    schedule = get_schedule(
        sorted(months)
    )

    race_map = {}

    for race in schedule["RaceList"]:

        key = (
            datetime.strptime(
                race["kaisaiDate"],
                "%Y%m%d"
            ).strftime("%Y-%m-%d"),
            race["keirinjoName"].replace("競輪場", ""),
        )

        race_map[key] = race

    # -----------------------------
    # 更新データ作成
    # -----------------------------
    update_records = []

    for event_date, venue, *_ in events:

        key = (
            event_date,
            venue,
        )

        race = race_map.get(key)

        if race is None:
            continue

        update_records.append({

            "date": event_date,

            "venue": venue,

            "grade": race["gradeIconName"],

            "kubun": race["kubunIconName"],

            "nichiji": race["nichijiIconName"],

        })

    update_event_info(
        update_records
    )

    return len(update_records)
