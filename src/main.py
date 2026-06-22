from excel_reader import get_today_tracks

tracks = get_today_tracks()
def get_today_tracks():
    return [
        "玉野",
        "岸和田"
    ]

print("開催場数:", len(tracks))
print(tracks)
