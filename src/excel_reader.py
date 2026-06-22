from calendar import monthrange
from datetime import date

from openpyxl import load_workbook


TARGET_BLOCKS = [
    "玉野",
    "現金機＆CLAP"
]


def get_merged_value(ws, cell):

    if cell.value is not None:
        return cell.value

    for merged in ws.merged_cells.ranges:

        if cell.coordinate in merged:

            parent = ws.cell(
                merged.min_row,
                merged.min_col
            )

            return parent.value

    return None


def find_months(ws):

    months = {}

    for row in ws.iter_rows():

        for cell in row:

            value = get_merged_value(
                ws,
                cell
            )

            if not isinstance(value, str):
                continue

            value = (
                value
                .replace(" ", "")
                .replace("　", "")
                .strip()
            )

            if not value.endswith("月"):
                continue

            try:

                month = int(
                    value.replace("月", "")
                )

                if 1 <= month <= 12:

                    months[month] = cell

            except:
                pass

    return months


def get_day1_column(
    ws,
    month_cell
):

    for merged in ws.merged_cells.ranges:

        if month_cell.coordinate in merged:

            return (
                merged.max_col + 1
            )

    return month_cell.column + 1


def resolve_year(month):

    # R8年度対応
    fiscal_year = 2026

    if month >= 4:
        return fiscal_year

    return fiscal_year + 1


def extract_venues(
    ws,
    target_col
):

    venues = []

    current_block = None

    for row in range(
        1,
        ws.max_row + 1
    ):

        block_name = get_merged_value(
            ws,
            ws.cell(row, 2)
        )

        if isinstance(block_name, str):

            block_name = block_name.strip()

            if block_name in TARGET_BLOCKS:

                current_block = block_name
                continue

        if current_block not in TARGET_BLOCKS:
            continue

        value = get_merged_value(
            ws,
            ws.cell(
                row,
                target_col
            )
        )

        if value is None:
            continue

        value = str(value).strip()

        if value == "":
            continue

        if value == "開催なし":
            continue

        if value in TARGET_BLOCKS:
            continue

        venues.append(value)

    return venues


def parse_excel(excel_path):

    wb = load_workbook(
        excel_path,
        data_only=True
    )

    records = []

    for ws in wb.worksheets:

        month_map = find_months(ws)

        for month, month_cell in month_map.items():

            year = resolve_year(
                month
            )

            day1_col = get_day1_column(
                ws,
                month_cell
            )

            days_in_month = monthrange(
                year,
                month
            )[1]

            for day in range(
                1,
                days_in_month + 1
            ):

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
