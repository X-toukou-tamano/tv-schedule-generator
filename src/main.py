import requests

DAY_CODES = {"1"}
NIGHT_CODES = {"3"}

def get_today_tracks():
    url = (
        "https://keirin.jp/pc/json"
        "?kaisaibikbn=0"
        "&kanyusyaflg=false"
        "&shccp=0"
        "&dispid=PJ0315"
        "&type=JSJ048"
    )

    data = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    ).json()

    day = []
    night = []

    for race in data["RaceList"]:

        code = race["kubunIconName"]

        if code not in DAY_CODES and code not in NIGHT_CODES:
            continue

        item = {
            "name": race["keirinjoName"],
            "grade": race["gradeIconName"],
            "status": race["nichijiIconName"],
        }

        if code in NIGHT_CODES:
            night.append(item)
        else:
            day.append(item)

    return day, night


day, night = get_today_tracks()

print("DAY")
print(day)

print("NIGHT")
print(night)
