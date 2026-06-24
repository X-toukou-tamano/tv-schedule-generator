import datetime

from database import get_events
from event_sorter import split_and_sort_events
from keirin_json import get_race_data

def get_today_sorted_data():
"""
本日開催データ取得
"""

```
rows = get_events()

today_str = datetime.date.today().isoformat()

vinfo_map = {}

try:

    race_data = get_race_data()

    if race_data and "RaceList" in race_data:

        for info in race_data["RaceList"]:

            venue_name = info.get(
                "keirinjoName"
            )

            if venue_name:

                vinfo_map[
                    venue_name
                ] = info

except Exception:

    pass

today_merged_data = []

for row in rows:

    event_date = row[0]
    venue_name = row[1]

    if (
        event_date == today_str
        and venue_name in vinfo_map
    ):

        info = vinfo_map[
            venue_name
        ]

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

        today_merged_data.append(
            {
                "name": venue_name,
                "session": session_type,
                "grade": grade_text,
                "status": status_text,
            }
        )

day_events, night_events = split_and_sort_events(
    today_merged_data
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

return (
    (
        day_events,
        night_events,
        preview_day,
        preview_night,
    ),
    today_str,
)
```

