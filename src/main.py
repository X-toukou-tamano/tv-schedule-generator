from keirin_json import get_race_data

data = get_race_data()

for race in data["RaceList"]:

    print("場:", race["keirinjoName"])
    print("グレード:", race["gradeIconName"])
    print("何日目:", race["nichijiIconName"])
    print("区分:", race["kubunIconName"])
    print("------------------")
