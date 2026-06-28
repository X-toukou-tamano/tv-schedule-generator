# keirin_schedule.py

import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://keirin.jp/pc/raceschedule"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

GRADE_MAP = {
    "ico_gp.png": "GP",
    "ico_g1.png": "G1",
    "ico_g2.png": "G2",
    "ico_g3.png": "G3",
    "ico_f1.png": "F1",
    "ico_f2.png": "F2",
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

            day = 1

            for td in cols[1:]:

                colspan = int(td.get("colspan", 1))

                grade_img = td.select_one("img.gradeIconSize")

                if grade_img:

                    # ---------- グレード ----------
                    grade = "-"

                    src = grade_img["src"]

                    for k, v in GRADE_MAP.items():

                        if k in src:
                            grade = v
                            break

                    # ---------- 開催区分 ----------
                    kubun = ""

                    hold = td.select_one("img.HoldingIconSize")

                    if hold:

                        m = re.search(
                            r'ico_kaisai_(\d+)\.png',
                            hold["src"]
                        )

                        if m:
                            kubun = m.group(1)

                    # ---------- encp ----------
                    encp = ""

                    a = td.find("a")

                    if a:

                        encp = a.get(
                            "data-pprm-encp",
                            ""
                        )

                    schedules.append({

                        "year": year,
                        "month": month,

                        "place": place,

                        "start_day": day,

                        "length": colspan,

                        "grade": grade,

                        "kubun": kubun,

                        "encp": encp,

                    })

                day += colspan

    return schedules


def get_schedule(months):

    result = []

    for year, month in months:

        print(f"{year}/{month} 取得中...")

        result.extend(
            parse_month(year, month)
        )

    return result


if __name__ == "__main__":

    months = [

        (2026, 9),

    ]

    data = get_schedule(months)

    for d in data:

        print(d)
