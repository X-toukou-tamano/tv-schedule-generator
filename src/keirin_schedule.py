# keirin_schedule.py

import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://keirin.jp/pc/raceschedule"
RACELIST_URL = "https://keirin.jp/pc/racelist"

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


def fetch_racelist(encp):

    r = requests.post(
        RACELIST_URL,
        data={
            "encp": encp,
            "disp": "PJ0301"
        },
        headers=HEADERS,
        timeout=30
    )

    r.raise_for_status()

    return r.text


def get_race_data(months):

    race_list = []

    for year, month in months:

        html = get_month_html(year, month)

        soup = BeautifulSoup(html, "html.parser")

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

                        grade = "-"

                        src = grade_img["src"]

                        for k, v in GRADE_MAP.items():

                            if k in src:
                                grade = v
                                break

                        hold_img = td.select_one("img.HoldingIconSize")

                        kubun = ""

                        if hold_img:

                            m = re.search(
                                r'ico_kaisai_(\d+)\.png',
                                hold_img["src"]
                            )

                            if m:
                                kubun = m.group(1)

                        a = td.find("a")

                        encp = ""

                        if a:

                            encp = a.get(
                                "data-pprm-encp",
                                ""
                            )

                        print(
                            place,
                            grade,
                            kubun,
                            encp
                        )

                        #
                        # 次ここで
                        #
                        # racelist_html = fetch_racelist(encp)
                        #
                        # ↓
                        #
                        # 初日
                        # 2日目
                        # 最終日
                        #
                        # を取得して
                        #
                        # RaceListへ追加する
                        #

                    day += colspan

    return {
        "RaceList": race_list
    }


if __name__ == "__main__":

    data = get_race_data(
        [
            (2026, 9),
        ]
    )

    print(data)
