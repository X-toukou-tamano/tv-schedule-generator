import requests
from bs4 import BeautifulSoup

URL = "https://keirin.jp/pc/raceschedule"

GRADE_MAP = {
    "ico_gp.png": "GP",
    "ico_g1.png": "G1",
    "ico_g2.png": "G2",
    "ico_g3.png": "G3",
    "ico_f1.png": "F1",
    "ico_f2.png": "F2",
}

NIGHT_VENUES = {
    "小倉",
    "玉野",
    "岐阜",
    "武雄",
    "佐世保",
    "高知",
    "松山",
    "別府",
    "久留米",
}


def get_schedule_data():

    html = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30,
    ).text

    soup = BeautifulSoup(html, "html.parser")

    year = soup.find(id="dispYearData")["value"]
    month = soup.find(id="dispDayData")["value"]

    result = {}

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

                    src = grade_img["src"]

                    grade = "-"

                    for k, v in GRADE_MAP.items():

                        if k in src:
                            grade = v
                            break

                    session = (
                        "night"
                        if place in NIGHT_VENUES
                        else "day"
                    )

                    for offset in range(colspan):

                        target_day = day + offset

                        date_str = (
                            f"{year}-{month}-{target_day:02d}"
                        )

                        if offset == colspan - 1:
                            status = "最終日"
                        else:
                            status = f"{offset + 1}日目"

                        result[
                            (date_str, place)
                        ] = {
                            "grade": grade,
                            "status": status,
                            "session": session,
                        }

                day += colspan

    return result


if __name__ == "__main__":

    schedule = get_schedule_data()

    for key, value in sorted(schedule.items()):

        print(
            key,
            value,
        )
