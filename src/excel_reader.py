import os
import re
from calendar import monthrange
from datetime import date
from openpyxl import load_workbook

TARGET_BLOCKS = [
    "玉野",
    "現金機＆CLAP"
]

IGNORE_VALUES = [
    "開催なし",
    "発売中止",
    "その他",
    "備考"
]

def build_merged_map(ws):
    merged_map = {}
    for merged in ws.merged_cells.ranges:
        min_col, min_row, max_col, max_row = merged.bounds
        parent_val = ws.cell(min_row, min_col).value
        for r in range(min_row, max_row + 1):
            for c in range(min_col, max_col + 1):
                merged_map[(r, c)] = parent_val
    return merged_map

def get_merged_value(cell, merged_map):
    if cell.value is not None:
        return cell.value
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
    fiscal_year = 2026 
    
    # 1. 西暦(4桁)がファイル名にあれば最優先
    match_year = re.search(r'(20\d{2})', filename)
    if match_year:
        fiscal_year = int(match_year.group(1))
    else:
        # 2. なければ R〇 から計算
        match_r = re.search(r'R([0-9０-９]+)', filename, re.IGNORECASE)
        if match_r:
            r_num = int(match_r.group(1).translate(str.maketrans('０１２３４５６７８９', '0123456789')))
            fiscal_year = 2018 + r_num

    if month >= 4:
        return fiscal_year
    return fiscal_year + 1

def clean_block_name(name):
    """表記揺れを吸収するためのヘルパー関数"""
    if not isinstance(name, str):
        return name
    # 全角半角スペースを除去し、半角&を全角＆に統一
    return name.replace(" ", "").replace(" ", "").replace("&", "＆").strip()

def find_block_column(ws, merged_map):
    """
    列固定禁止仕様への対応：
    「玉野」や「現金機＆CLAP」などのブロック名が書かれている列を動的に探す
    """
    for row in range(1, min(ws.max_row + 1, 100)):
        for col in range(1, 10):
            val = get_merged_value(ws.cell(row, col), merged_map)
            cleaned_val = clean_block_name(val)
            if isinstance(cleaned_val, str) and cleaned_val in TARGET_BLOCKS:
                print(f"  -> [DEBUG] Target block found at column {col} (Matched: {cleaned_val})")
                return col
                
    print("  -> [DEBUG] Target block NOT found! Defaulting to column 2.")
    return 2 

def extract_venues(ws, target_col, block_col, merged_map):
    venues = []
    current_block = None

    for row in range(1, ws.max_row + 1):
        block_name = get_merged_value(ws.cell(row, block_col), merged_map)
        cleaned_block = clean_block_name(block_name)

        if isinstance(cleaned_block, str):
            if cleaned_block != "":
                if cleaned_block in TARGET_BLOCKS:
                    current_block = cleaned_block
                    # 【修正】ここにあった continue を削除しました！
                    # 結合セルの場合、この行自体に開催場データがあるため読み飛ばしてはいけない
                else:
                    # ターゲット以外のブロック（サテライト等）に入ったらリセット
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
        
        merged_map = build_merged_map(ws)
        month_map = find_months(ws, merged_map)
        
        if not month_map:
            print(f"  -> No months found in {ws.title}, skipping.")
            continue
            
        # シートごとにブロック名が記載されている列を取得
        block_col = find_block_column(ws, merged_map)

        for month, month_cell in month_map.items():
            year = resolve_year(filename, month)
            day1_col = get_day1_column(ws, month_cell)
            days_in_month = monthrange(year, month)[1]

            print(f"  -> Extracting: {year}年{month}月 (days: {days_in_month})")

            for day in range(1, days_in_month + 1):
                target_col = day1_col + day - 1
                
                # 動的に取得した block_col を渡す
                venues = extract_venues(ws, target_col, block_col, merged_map)

                for venue in venues:
                    records.append({
                        "date": date(year, month, day),
                        "venue": venue
                    })
                    
    print(f"[LOG] parse_excel completed. Total records extracted: {len(records)}")
    return records
