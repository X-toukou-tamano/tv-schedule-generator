import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

URL = "https://keirin.jp/pc/raceschedule"

GRADE_MAP = {
    "ico_gp.png": "GP",
    "ico_g1.png": "G1",
    "ico_g2.png": "G2",
    "ico_g3.png": "G3",
    "ico_f1.png": "F1",
    "ico_f2.png": "F2",
}


def grade_from_img(src):
    for k, v in GRADE_MAP.items():
        if k in src:
            return v
    return "不明"


def is_night(place):
    """現状はナイター場判定（必要に応じて追加）"""
    night = {
        "小倉","玉野","岐阜","武雄","佐世保",
        "高知","松山","別府","久留米"
    }
    return place in night


def parse():

    html = requests.get(URL).text
    soup = BeautifulSoup(html, "html.parser")

    results = []

    tables = soup.select("table.chiku_tbl")

    for table in tables:

        rows = table.select("tbody tr")

        for row in rows:

            tds = row.find_all("td")

            if len(tds) < 2:
                continue

            place = tds[0].get_text(strip=True)

            day = 1

            for td in tds[1:]:

                colspan = int(td.get("colspan", 1))

                img = td.select_one("img.gradeIconSize")

                if img:

                    grade = grade_from_img(img["src"])

                    start = day
                    length = colspan
                    end = start + length - 1

                    schedule = []

                    for i in range(length):

                        d = start + i

                        if i == length - 1:
                            status = "最終日"
                        else:
                            status = f"{i+1}日目"

                        schedule.append({
                            "day": d,
                            "status": status
                        })

                    results.append({
                        "place": place,
                        "grade": grade,
                        "type": "ナイター" if is_night(place) else "デイ",
                        "start": start,
                        "end": end,
                        "length": length,
                        "schedule": schedule
                    })

                day += colspan

    return results


if __name__ == "__main__":

    data = parse()

    for race in data:

        print("="*50)
        print(race["place"])
        print("グレード :", race["grade"])
        print("開催 :", race["type"])
        print(f"{race['start']}日～{race['end']}日 ({race['length']}日間)")

        for d in race["schedule"]:
            print(f"  {d['day']}日 : {d['status']}")
