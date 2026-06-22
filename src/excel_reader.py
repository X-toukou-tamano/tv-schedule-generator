import os
import re
from calendar import monthrange
from datetime import date
from openpyxl import load_workbook

TARGET_BLOCKS = [
    "玉野",
    "現金機＆CLAP"
]

# ⑧ 不要データ除外リストを追加
IGNORE_VALUES = [
    "開催なし",
    "発売中止",
    "その他",
    "備考"
]

def build_merged_map(ws):
    """
    ①・② 高速化用：シート内の結合セルを最初に1度だけ走査し、
    (row, col) をキーとした親セルの値の辞書を作成する
    """
    merged_map = {}
    for merged in ws.merged_cells.ranges:
        min_col, min_row, max_col, max_row = merged.bounds
        parent_val = ws.cell(min_row, min_col).value
        for r in range(min_row, max_row + 1):
            for c in range(min_col, max_col + 1):
                merged_map[(r, c)] = parent_val
    return merged_map

def get_merged_value(cell, merged_map):
    """高速化された結合セル値取得"""
    if cell.value is not None:
        return cell.value
    # 結合セル辞書から取得（O(1)で済むため圧倒的に速い）
    return merged_map.get((cell.row, cell.column), None)

def find_months(ws, merged_map):
    months = {}
    for row in ws.iter_rows():
        for cell in row:
            value = get_merged_value(cell, merged_map)

            if not isinstance(value, str):
                continue

            value = value.replace(" ", "").replace(" ", "").strip()

            if not value.endswith("月"):
                continue

            try:
                month = int(value.replace("月", ""))
                if 1 <= month <= 12:
                    # ⑥ 重複対策：すでに見つかっている月は上書きしない（先勝ち）
                    if month not in months:
                        months[month] = cell
            except ValueError:
                pass
    return months

def get_day1_column(ws, month_cell):
    for merged in ws.merged_cells.ranges:
        if month_cell.coordinate in merged:
            return merged.max_col + 1
    return month_cell.column + 1

def resolve_year(filename, month):
    """
    ⑤ 年度の動的取得：ファイル名から「R〇」を抽出して西暦を計算
    """
    # デフォルトは2026年とする（万が一取得できなかった場合のフォールバック）
    fiscal_year = 2026 
    
    # ファイル名から "R8" や "R７" 等を抽出（全角・半角対応）
    match = re.search(r'R([0-9０-９]+)', filename, re.IGNORECASE)
    if match:
        # 全角数字を半角に変換し、2018を足して西暦にする (例: R8 -> 8 + 2018 = 2026)
        r_num = int(match.group(1).translate(str.maketrans('０１２３４５６７８９', '0123456789')))
        fiscal_year = 2018 + r_num

    # 4月〜12月はその年、1月〜3月は翌年扱い
    if month >= 4:
        return fiscal_year
    return fiscal_year + 1

def extract_venues(ws, target_col, merged_map):
    venues = []
    current_block = None

    for row in range(1, ws.max_row + 1):
        block_name = get_merged_value(ws.cell(row, 2), merged_map)

        if isinstance(block_name, str):
            block_name = block_name.strip()
            if block_name != "":
                if block_name in TARGET_BLOCKS:
                    current_block = block_name
                    continue
                else:
                    # ③ ブロック終了判定：ターゲット以外のブロック名（サテライト等）が出たらリセット
                    current_block = None

        if current_block not in TARGET_BLOCKS:
            continue

        value = get_merged_value(ws.cell(row, target_col), merged_map)

        if value is None:
            continue

        value = str(value).strip()

        if value == "" or value in IGNORE_VALUES or value in TARGET_BLOCKS:
            continue

        venues.append(value)

    return venues

def parse_excel(excel_path):
    print(f"[LOG] parse_excel start: {excel_path}")
    
    filename = os.path.basename(excel_path)
    
    wb = load_workbook(excel_path, data_only=True)
    print(f"[LOG] workbook loaded successfully. Sheets: {wb.sheetnames}")

    records = []

    for ws in wb.worksheets:
        print(f"[LOG] Processing sheet: {ws.title}")
        
        # ①・② シートごとに結合セルのマップを作成（高速化の要）
        merged_map = build_merged_map(ws)
        
        month_map = find_months(ws, merged_map)
        if not month_map:
            print(f"  -> No months found in {ws.title}, skipping.")
            continue

        for month, month_cell in month_map.items():
            year = resolve_year(filename, month)
            day1_col = get_day1_column(ws, month_cell)
            days_in_month = monthrange(year, month)[1]

            print(f"  -> Extracting: {year}年{month}月 (days: {days_in_month})")

            for day in range(1, days_in_month + 1):
                target_col = day1_col + day - 1
                venues = extract_venues(ws, target_col, merged_map)

                for venue in venues:
                    records.append({
                        "date": date(year, month, day),
                        "venue": venue
                    })
                    
    print(f"[LOG] parse_excel completed. Total records extracted: {len(records)}")
    return records
