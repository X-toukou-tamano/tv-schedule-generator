import os
import re
import unicodedata
from calendar import monthrange
from datetime import date
from openpyxl import load_workbook

# 全国の競輪場43場リスト（名称クリーニング用）
KEIRIN_TRACKS = [
    "函館", "青森", "いわき平", "弥彦", "前橋", "取手", "宇都宮", "大宮", "西武園", "京王閣", "立川",
    "松戸", "千葉", "川崎", "平塚", "小田原", "伊東", "静岡", "名古屋", "岐阜", "大垣", "豊橋", "富山",
    "松阪", "四日市", "福井", "奈良", "向日町", "和歌山", "岸和田", "玉野", "広島", "防府", "高松", "小松島",
    "高知", "松山", "小倉", "久留米", "武雄", "佐世保", "別府", "熊本"
]

# 取得対象のブロック名
TARGET_BLOCKS = [
    "玉野",
    "現金機＆CLAP"
]

# 取得を除外する文字列
IGNORE_VALUES = [
    "開催なし",
    "発売中止",
    "その他",
    "備考"
]

def clean_block_name(name):
    """ブロック名の全角半角やスペースなどの表記揺れを吸収する"""
    if not isinstance(name, str):
        return name
    name = unicodedata.normalize('NFKC', name)
    name = name.replace(" ", "").replace(" ", "").strip()
    name = name.replace("&", "＆")
    return name

def build_merged_map(ws):
    """結合セルの値を事前マッピングして高速化＆エラー回避"""
    merged_map = {}
    for merged in ws.merged_cells.ranges:
        min_col, min_row, max_col, max_row = merged.bounds
        parent_val = ws.cell(min_row, min_col).value
        for r in range(min_row, max_row + 1):
            for c in range(min_col, max_col + 1):
                merged_map[(r, c)] = parent_val
    return merged_map

def get_merged_value(cell, merged_map):
    """セルが結合されていれば親の値を返し、そうでなければ自身の値を返す"""
    if cell.value is not None:
        return cell.value
    return merged_map.get((cell.row, cell.column), None)

def find_months(ws, merged_map):
    """シート全体から「○月」のセルを探し出す"""
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
    """月セルの横幅（結合）を計算し、1日の列を特定する"""
    for merged in ws.merged_cells.ranges:
        if month_cell.coordinate in merged:
            return merged.max_col + 1
    return month_cell.column + 1

def resolve_year(filename, month):
    """ファイル名から年度を割り出し、月ごとの西暦を正確に計算する"""
    fiscal_year = 2026 
    match_year = re.search(r'(20\d{2})', filename)
    if match_year:
        fiscal_year = int(match_year.group(1))
    else:
        match_r = re.search(r'R([0-9０-９]+)', filename, re.IGNORECASE)
        if match_r:
            r_num = int(match_r.group(1).translate(str.maketrans('０１２３４５６７８９', '0123456789')))
            fiscal_year = 2018 + r_num

    # 4月以降はその年の西暦、1〜3月は年を跨ぐので+1する
    if month >= 4:
        return fiscal_year
    return fiscal_year + 1

def find_block_column(ws, merged_map):
    """「玉野」などのブロック名が何列目にあるかを動的に探す"""
    for row in range(1, min(ws.max_row + 1, 100)):
        for col in range(1, 10):
            val = get_merged_value(ws.cell(row, col), merged_map)
            cleaned_val = clean_block_name(val)
            if isinstance(cleaned_val, str) and cleaned_val in TARGET_BLOCKS:
                return col
    return 2 

def normalize_venue_name(raw_name):
    """場名をクリーニングする（Gや記念を消し、1-1などは玉野に変換）"""
    if not isinstance(raw_name, str):
        return raw_name
        
    name = unicodedata.normalize('NFKC', raw_name)
    name_no_space = name.replace(" ", "").replace(" ", "")

    # 「1-1」など数字とハイフンのみの場合は「玉野」にする
    if re.match(r'^\d+-\d+$', name_no_space):
        return "玉野"

    # リストにある場名が含まれていれば、その場名だけを抽出する（Gや記念を削ぎ落とす）
    for track in KEIRIN_TRACKS:
        if track in name_no_space:
            return track

    return raw_name

def extract_venues(ws, target_col, block_col, merged_map, start_row, end_row):
    """指定された月の行範囲（start_row 〜 end_row）だけで開催場を抽出する"""
    venues = []
    current_block = None

    for row in range(start_row, end_row + 1):
        block_name = get_merged_value(ws.cell(row, block_col), merged_map)
        cleaned_block = clean_block_name(block_name)

        # ブロック名の判定：「出走表」や「サテライト」等が出たらOFFにする
        if isinstance(cleaned_block, str) and cleaned_block != "":
            if cleaned_block in TARGET_BLOCKS:
                current_block = cleaned_block
            else:
                current_block = None
        else:
            current_block = None

        if current_block not in TARGET_BLOCKS:
            continue

        value = get_merged_value(ws.cell(row, target_col), merged_map)

        if value is None:
            continue

        value = str(value).strip()

        if value == "" or value in IGNORE_VALUES or value in TARGET_BLOCKS:
            continue

        # 場名を綺麗にしてから追加
        cleaned_venue = normalize_venue_name(value)
        venues.append(cleaned_venue)

    return venues

def parse_excel(excel_path):
    print(f"[LOG] parse_excel start: {excel_path}")
    
    filename = os.path.basename(excel_path)
    wb = load_workbook(excel_path, data_only=True)
    print(f"[LOG] workbook loaded successfully.")

    records = []
    # 複数シートがあっても一番最初のシートだけを処理する
    ws = wb.worksheets[0]
    
    merged_map = build_merged_map(ws)
    month_map = find_months(ws, merged_map)
    
    if not month_map:
        return records
        
    block_col = find_block_column(ws, merged_map)

    # 月を行番号の順（上から下）に並び替える
    sorted_months = sorted(month_map.items(), key=lambda item: item[1].row)

    for i, (month, month_cell) in enumerate(sorted_months):
        year = resolve_year(filename, month)
        day1_col = get_day1_column(ws, month_cell)
        days_in_month = monthrange(year, month)[1]

        # 今の月の開始行を設定
        start_row = month_cell.row
        
        # 次の月があればその「1行上」を終わりにする（月の壁）
        if i + 1 < len(sorted_months):
            end_row = sorted_months[i+1][1].row - 1
        else:
            # 最後の月ならエクセルの一番下まで
            end_row = ws.max_row

        print(f"  -> Extracting: {year}年{month}月 (days: {days_in_month}, rows: {start_row}-{end_row})")

        for day in range(1, days_in_month + 1):
            target_col = day1_col + day - 1
            # 指定された月の範囲の中だけで1日分のデータをかき集める
            venues = extract_venues(ws, target_col, block_col, merged_map, start_row, end_row)

            for venue in venues:
                records.append({
                    "date": date(year, month, day),
                    "venue": venue
                })
                    
    print(f"[LOG] parse_excel completed. Total records extracted: {len(records)}")
    return records
