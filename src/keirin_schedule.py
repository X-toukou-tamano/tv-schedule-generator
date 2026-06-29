import json
import re
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://keirin.jp/pc/raceschedule"
HEADERS = {"User-Agent": "Mozilla/5.0"}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

def get_month_html(year, month):
    url = f"{BASE_URL}?scyy={year}&scym={month:02d}"

    r = SESSION.get(
        url,
        timeout=30,
    )

    r.raise_for_status()

    return r.text


def get_racelist(encp):
    r = SESSION.post(
        "https://keirin.jp/pc/racelist",
        data={
            "encp": encp,
            "disp": "PJ0301",
        },
        timeout=30,
    )

    print("=" * 80)
    print("status :", r.status_code)
    print("url    :", r.url)
    print("encp   :", encp)
    print(r.text[:1000])
    print("=" * 80)

    # r.raise_for_status()

    html = r.text

    m1 = re.search(r"jsonData\['PC0201'\]\s*=\s*(\{[\s\S]*?\});", html)
    m2 = re.search(r"jsonData\['PJ0301'\]\s*=\s*(\{[\s\S]*?\});", html)

    if m1 is None:
        raise RuntimeError("PC0201 が見つかりません")
    if m2 is None:
        raise RuntimeError("PJ0301 が見つかりません")

    return {
        "PC0201": json.loads(m1.group(1)),
        "PJ0301": json.loads(m2.group(1)),
    }
def parse_month(year, month):
    html = get_month_html(year, month)
    soup = BeautifulSoup(html, "html.parser")

    schedules = []
    tables = soup.select("table.chiku_tbl")

    for table in tables:
        tbody = table.find("tbody")
        if tbody is None:
            continue

        rows = tbody.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue

            place = cols[0].get_text(strip=True)

            for td in cols[1:]:
                if td.select_one("img.gradeIconSize"):
                    a = td.find("a")
                    holding = td.select_one("img.HoldingIconSize")

                    if holding:
                        src = holding.get("src", "")
                        if "ico_kaisai_3" in src:
                            kubun = "3"
                        elif "ico_kaisai_5" in src:
                            kubun = "5"
                        elif "ico_kaisai_8" in src:
                            kubun = "8"
                        else:
                            kubun = "1"
                    else:
                        # HoldingIconが無い開催＝デイ
                        kubun = "1"

                    schedules.append({
                        "place": place,
                        "encp": a.get("data-pprm-encp", "") if a else "",
                        "kubun": kubun,
                    })

    return schedules


def get_schedule(months):
    race_list = []

    for year, month in months:
        schedules = parse_month(year, month)

        # ★まず最初の1件だけ確認
        print("最初のschedule =", schedules[0])

        for s in schedules:
            if not s["encp"]:
                continue

            try:
                obj = get_racelist(s["encp"])
            except Exception as e:
                # 将来的に logging へ置き換え予定
                print(f"RaceList取得失敗 {s['place']} : {e}")
                break

            pc = obj["PC0201"]["C0201data"]
            start_date = datetime.strptime(pc["selKaisai"], "%Y%m%d")
            kubun = s["kubun"]

            for index, d in enumerate(pc["C0201kaisai"]):
                kaisai_date = (start_date + timedelta(days=index)).strftime("%Y%m%d")

                record = {
                    "kaisaiDate": kaisai_date,
                    "keirinjoName": s["place"],
                    "gradeIconName": pc.get("imgGradeAlt", ""),
                    "nichijiIconName": d["txtDaily"].replace("(", "").replace(")", ""),
                    "kubunIconName": kubun,
                    "raceName": pc.get("raceName", ""),
                }
                race_list.append(record)

    return {"RaceList": race_list}