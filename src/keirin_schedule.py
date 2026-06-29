import json
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://keirin.jp/pc/raceschedule"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_month_html(year, month):
    url = f"{BASE_URL}?scyy={year}&scym={month:02d}"
    r = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )
    r.raise_for_status()
    return r.text
def get_racelist(encp):
    r = requests.post(
        "https://keirin.jp/pc/racelist",
        headers=HEADERS,
        data={
            "encp": encp,
            "disp": "PJ0301",
        },
        timeout=30,
    )
    r.raise_for_status()
    html = r.text

    m1 = re.search(
        r"jsonData\['PC0201'\]\s*=\s*(\{[\s\S]*?\});",
        html,
    )

    m2 = re.search(
        r"jsonData\['PJ0301'\]\s*=\s*(\{[\s\S]*?\});",
        html,
    )

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
                # img.gradeIconSize があればレース開催日とみなす
                if td.select_one("img.gradeIconSize"):
                    encp = ""
                    a = td.find("a")
                    if a:
                        encp = a.get("data-pprm-encp", "")

                    schedules.append({
                        "place": place,
                        "encp": encp,
                    })

    return schedules


def get_schedule(months):
    race_list = []

    for year, month in months:
        print(f"{year}/{month} 取得中...")
        schedules = parse_month(year, month)

        for s in schedules:
            if not s["encp"]:
                continue

            try:
                obj = get_racelist(s["encp"])
            except Exception as e:
                print(f"RaceList取得失敗 {s['place']} : {e}")
                continue

            for race in obj.get("RaceList", []):
                race_list.append({
                    "kaisaiDate": race["kaisaiDate"],
                    "keirinjoName": race["keirinjoName"],
                    "gradeIconName": race["gradeIconName"],
                    "nichijiIconName": race["nichijiIconName"],
                    "kubunIconName": race["kubunIconName"],
                })

    return {
        "RaceList": race_list
    }
