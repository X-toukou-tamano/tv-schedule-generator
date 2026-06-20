import requests
from bs4 import BeautifulSoup

url = "https://keirin.jp/pc/top"

html = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
).text

soup = BeautifulSoup(html, "html.parser")

for script in soup.find_all("script"):
    src = script.get("src")
    if src:
        print(src)
