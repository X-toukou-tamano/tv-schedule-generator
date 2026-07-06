from database import (
    create_tables,
    save_records,
    save_update_time,
)

from excel_reader import parse_excel
from schedule_updater import update_schedule_info

EXCEL_FILE = "excel_data/R8_上期.xlsx"   # 必要に応じて変更

create_tables()

records = parse_excel(EXCEL_FILE)

save_records(records)

update_schedule_info()

save_update_time()

print(f"{len(records)}件 更新完了")
