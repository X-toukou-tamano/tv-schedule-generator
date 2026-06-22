from datetime import date
from openpyxl import load_workbook


TARGET_BLOCKS = [
    "玉野",
    "現金機＆CLAP"
]


def parse_excel(excel_path):

    wb = load_workbook(
        excel_path,
        data_only=True
    )

    records = []

    for ws in wb.worksheets:

        month_map = find_months(ws)

        for month, month_cell in month_map.items():

            day1_col = get_day1_column(
                ws,
                month_cell
            )

            days_in_month = 31

            for day in range(1, days_in_month + 1):

                target_col = (
                    day1_col +
                    day -
                    1
                )

                venues = extract_venues(
                    ws,
                    target_col
                )

                for venue in venues:

                    year = resolve_year(month)

                    records.append(
                        {
                            "date": date(
                                year,
                                month,
                                day
                            ),
                            "venue": venue
                        }
                    )

    return records
def get_today_tracks():
    return []
