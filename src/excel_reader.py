from datetime import datetime
from openpyxl import load_workbook

def get_today_tracks():

    today = datetime.today()

    print("月:", today.month)
    print("日:", today.day)

    wb = load_workbook(
        "R８上期確定版(サテライト込み)_2026.02.14.xlsx",
        data_only=True
    )

    for sheet_name in wb.sheetnames:
        print(sheet_name)

    return []
