import requests

files = [
    "/pc/static/js/commonJSON.js",
    "/pc/static/js/PC0101.js",
    "/pc/static/js/PC0101_v.js",
    "/pc/static/js/PC0101_c.js",
    "/pc/static/js/PC0102.js",
]

for f in files:
    url = "https://keirin.jp" + f

    print("\n" + "=" * 80)
    print(url)
    print("=" * 80)

    r = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    print(r.text[:5000])
