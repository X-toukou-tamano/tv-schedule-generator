from datetime import datetime
from openpyxl import load_workbook

def get_today_tracks():

    today = datetime.today()

    print("月:", today.month)
    print("日:", today.day)

    return []
