import requests
import re

targets = [
    "https://keirin.jp/pc/static/js/commonJSON.js",
    "https://keirin.jp/pc/static/js/PC0101.js",
    "https://keirin.jp/pc/static/js/PC0101_v.js",
    "https://keirin.jp/pc/static/js/PC0101_c.js",
]

patterns = [
    r'https?://[^"\']+',
    r'/[A-Za-z0-9_/\-\.]+json[A-Za-z0-9_/\-\.]*',
    r'/[A-Za-z0-9_/\-\.]+xml[A-Za-z0-9_/\-\.]*',
]

for url in targets:
    print("\n" + "=" * 80)
    print(url)
    print("=" * 80)

    text = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    ).text

    for p in patterns:
        for m in re.findall(p, text, re.IGNORECASE):
            print(m)
