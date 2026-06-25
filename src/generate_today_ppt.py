import os
from datetime import datetime
from zoneinfo import ZoneInfo

from database import (
    create_tables,
    get_summary,
    save_records,
)

from excel_reader import parse_excel
from today_service import get_today_sorted_data
from ppt_generator import create_powerpoint

def main():

    create_tables()

    summary = get_summary()

    if summary[2] == 0:

        today = datetime.now(
            ZoneInfo("Asia/Tokyo")
        ).date()

        if today.month >= 4:
            reiwa = today.year - 2018
        else:
            reiwa = today.year - 2019

        year = f"R{reiwa}"

        if 4 <= today.month <= 9:
            term = "上期"
        else:
            term = "下期"

        target_path = os.path.join(
            "uploads",
            f"{year}_{term}.xlsx"
        )

        if os.path.exists(
            target_path
        ):

            records = parse_excel(
                target_path
            )

            save_records(
                records
            )

    (
        (
            day_events,
            night_events,
            _,
            _,
        ),
        _,
    ) = get_today_sorted_data()

    create_powerpoint(
        day_events,
        night_events
    )

    print("PPT生成完了")
