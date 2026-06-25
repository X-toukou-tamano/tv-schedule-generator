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

        if 4 <= today.month <= 9:
            term = "上期"
        else:
            term = "下期"

        target_path = None

        if os.path.isdir("uploads"):

            for file_name in sorted(
                os.listdir("uploads"),
                reverse=True
            ):

                if (
                    file_name.endswith(".xlsx")
                    and term in file_name
                ):

                    target_path = os.path.join(
                        "uploads",
                        file_name
                    )

                    break

        if target_path:

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


if __name__ == "__main__":
    main()
