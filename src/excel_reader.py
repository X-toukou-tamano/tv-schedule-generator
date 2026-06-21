from datetime import datetime
from openpyxl import load_workbook


MONTHS = [
    "4月", "5月", "6月", "7月",
    "8月", "9月", "10月", "11月",
    "12月", "1月", "2月", "3月"
]

TARGET_BLOCKS = [
    "玉野",
    "現金機＆CLAP"
]


def get_cell_value(ws, row, col):
    cell = ws.cell(row=row, column=col)

    if cell.value is not None:
        return cell.value

    for merged in ws.merged_cells.ranges:
        if (
            merged.min_row <= row <= merged.max_row
            and merged.min_col <= col <= merged.max_col
        ):
            return ws.cell(
                merged.min_row,
                merged.min_col
            ).value

    return None


def find_month_cell(ws, month):

    target = f"{month}月"

    for row in ws.iter_rows():
        for cell in row:

            value = str(cell.value).strip() if cell.value else ""

            if value == target:
                return cell

    return None


def get_day1_column(ws, month_cell):

    col = month_cell.column

    for merged in ws.merged_cells.ranges:

        if (
            merged.min_row <= month_cell.row <= merged.max_row
            and merged.min_col <= col <= merged.max_col
        ):
            return merged.max_col + 1

    return col + 1


def find_block_rows(ws):

    blocks = {}

    for row in range(1, ws.max_row + 1):

        value = str(
            get_cell_value(ws, row, 1) or ""
        ).strip()

        if value in TARGET_BLOCKS:
            blocks[value] = row

    return blocks


def extract_tracks(ws, target_col):

    tracks = []

    blocks = find_block_rows(ws)

    for block_name, row in blocks.items():

        value = get_cell_value(ws, row, target_col)

        if not value:
            continue

        text = str(value).strip()

        if text == "開催なし":
            continue

        tracks.append(text)

    return tracks


def get_today_tracks():

    today = datetime.today()

    wb = load_workbook(
        "R８上期確定版(サテライト込み)_2026.02.14.xlsx",
        data_only=True
    )

    for sheet_name in wb.sheetnames:

        ws = wb[sheet_name]

        month_cell = find_month_cell(
            ws,
            today.month
        )

        if month_cell is None:
            continue

        day1_col = get_day1_column(
            ws,
            month_cell
        )

        target_col = (
            day1_col +
            today.day -
            1
        )

        tracks = extract_tracks(
            ws,
            target_col
        )

        if tracks:
            return tracks

    return []


if __name__ == "__main__":

    result = get_today_tracks()

    print(result)
