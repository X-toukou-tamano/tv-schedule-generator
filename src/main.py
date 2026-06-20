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

    item = {
        "name": race["keirinjoName"],
        "grade": race["gradeIconName"],
        "status": race["nichijiIconName"],
        "session": session
    }

    print(item)

    
