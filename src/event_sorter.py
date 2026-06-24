# 競輪場を「最も南にある場(インデックス0)」から「最も北にある場(インデックス最大)」の順に完全定義
# 同じグレード・同じ日数だった場合、このリストで前(数字が小さい)にある場が優先されます。
SOUTH_TO_NORTH_TRACKS = [
    "熊本", "佐世保", "武雄", "久留米", "小倉", "別府",
    "高知", "松山", "小松島", "高松",
    "防府", "広島", "玉野",
    "岸和田", "和歌山", "向日町", "奈良", "福井",
    "四日市", "松阪", "豊橋", "大垣", "岐阜", "名古屋",
    "静岡", "伊東", "小田原", "平塚", "川崎", "松戸",
    "立川", "京王閣", "西武園", "大宮", "宇都宮", "取手",
    "前橋", "富山", "弥彦", "いわき平",
    "青森", "函館"
]

# グレードの優先順位
# 数字が小さいほど上位表示
GRADE_PRIORITY = {
    "GP": 0,
    "GⅠ": 1,
    "G1": 1,
    "GⅡ": 2,
    "G2": 2,
    "GⅢ": 3,
    "G3": 3,
    "FⅠ": 4,
    "F1": 4,
    "FⅡ": 5,
    "F2": 5,
}

# 日数の優先順位
# 数字が小さいほど進行している開催
STATUS_PRIORITY = {
    "最終日": 0,
    "4日目": 1,
    "3日目": 2,
    "2日目": 3,
    "初日": 4,
}


def get_event_sort_key(event):
    """
    並び順

    1. 玉野最優先
    2. グレード順
    3. 日数順
    4. 南→北順
    """

    name = event.get("name", "")
    grade = event.get("grade", "-")
    status = event.get("status", "-")

    # 玉野最優先
    is_tamano_priority = 0 if name == "玉野" else 1

    # グレード順
    grade_score = GRADE_PRIORITY.get(
        grade,
        99
    )

    # 日数順
    status_score = STATUS_PRIORITY.get(
        status,
        99
    )

    # 南→北順
    try:
        geo_score = SOUTH_TO_NORTH_TRACKS.index(
            name
        )
    except ValueError:
        geo_score = 999

    return (
        is_tamano_priority,
        grade_score,
        status_score,
        geo_score
    )


def split_and_sort_events(today_merged_data):
    """
    本日の開催情報を

    ・デイ
    ・ナイター

    に分離し、

    玉野優先
    ↓
    グレード順
    ↓
    日数順
    ↓
    南→北順

    でソートしたイベント辞書リストを返す
    """

    day_events = []
    night_events = []

    # デイ・ナイター仕分け
    for event in today_merged_data:

        if event["session"] == "day":
            day_events.append(event)

        elif event["session"] == "night":
            night_events.append(event)

    # ソート
    day_sorted = sorted(
        day_events,
        key=get_event_sort_key
    )

    night_sorted = sorted(
        night_events,
        key=get_event_sort_key
    )

    return (
        day_sorted,
        night_sorted
    )
