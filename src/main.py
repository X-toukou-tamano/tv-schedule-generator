import requests

url = "https://keirin.jp/pc/top"

response = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=30
)

print("status:", response.status_code)
print(response.text[:1000])
