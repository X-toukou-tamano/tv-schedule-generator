import requests
import json

url = "https://keirin.jp/pc/json?kaisaibikbn=0&kanyusyaflg=false&shccp=0&dispid=PJ0315&type=JSJ048"

data = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
).json()

for race in data["RaceList"]:
    print(
        race["keirinjoName"],
        race["gradeIconName"],
        race["nichijiIconName"],
        race["kubunIconName"]
    )
