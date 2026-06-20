from keirin_json import get_race_data

DAY_CODES = {"1"}
NIGHT_CODES = {"3"}

data = get_race_data()

for race in data["RaceList"]:

    code = race["kubunIconName"]

    if code in DAY_CODES:
        session = "day"

    elif code in NIGHT_CODES:
        session = "night"

    else:
        continue

    print("場:", race["keirinjoName"])
    print("グレード:", race["gradeIconName"])
    print("何日目:", race["nichijiIconName"])
    print("区分:", session)
    print("------------------")
