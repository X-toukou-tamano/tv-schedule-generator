from datetime import datetime
from openpyxl import load_workbook


TARGET_BLOCKS = [
    "玉野",
    "現金機＆CLAP"
]

ALL_BLOCKS = [
    "玉野",
    "現金機＆CLAP",
    "サテライト津山",
    "サテライト笠岡",
    "サテライト山陰",
    "ST津山"
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

    for merged in ws.merged_cells.ranges:

        if (
            merged.min_row <= month_cell.row <= merged.max_row
            and merged.min_col <= month_cell.column <= merged.max_col
        ):
            return merged.max_col + 1

    return month_cell.column + 1


def find_blocks(ws):

    blocks = []

    for row in range(1, ws.max_row + 1):
        for col in range(1, ws.max_column + 1):

            value = get_cell_value(ws, row, col)

            if value is None:
                continue

            text = str(value).strip()

            if text in ALL_BLOCKS:

                blocks.append(
                    {
                        "name": text,
                        "row": row
                    }
                )

                break

    blocks.sort(key=lambda x: x["row"])

    return blocks


def get_block_range(blocks, target_name):

    for idx, block in enumerate(blocks):

        if block["name"] != target_name:
            continue

        start_row = block["row"]

        if idx + 1 < len(blocks):
            end_row = blocks[idx + 1]["row"] - 1
        else:
            end_row = 99999

        return start_row, end_row

    return None


def extract_tracks(ws, target_col):

    tracks = []

    blocks = find_blocks(ws)

    for target_block in TARGET_BLOCKS:

        block_range = get_block_range(
            blocks,
            target_block
        )

        if block_range is None:
            continue

        start_row, end_row = block_range

        for row in range(start_row + 1, end_row + 1):

            value = get_cell_value(
                ws,
                row,
                target_col
            )

            if value is None:
                continue

            text = str(value).strip()

            if not text:
                continue

            if text == "開催なし":
                continue

            if text in ALL_BLOCKS:
                continue

            if text not in tracks:
                tracks.append(text)

    return tracks


def get_today_tracks(excel_path):

    today = datetime.today()

    wb = load_workbook(
        excel_path,
        data_only=True
    )

    for ws in wb.worksheets:

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

        return extract_tracks(
            ws,
            target_col
        )

    return []


if __name__ == "__main__":

    tracks = get_today_tracks(
        "R８上期確定版(サテライト込み)_2026.02.14.xlsx"
    )

    print(tracks)
