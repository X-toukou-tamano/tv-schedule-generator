import requests

DAY_CODES = {"1"}
NIGHT_CODES = {"3"}

def get_race_data():

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

    return data
