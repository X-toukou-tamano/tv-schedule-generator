from excel_reader import get_today_tracks

tracks = get_today_tracks()

print("開催場数:", len(tracks))
print(tracks)
