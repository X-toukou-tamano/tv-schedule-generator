# 競輪場を「最も南にある場(インデックス0)」から「最も北にある場(インデックス最大)」の順に完全定義
# 同じグレード・同じ日数だった場合、このリストで前(数字が小さい)にある場が優先されます。
SOUTH_TO_NORTH_TRACKS = [
    "熊本", "佐世保", "武雄", "久留米", "小倉", "別府", "高知", "松山", "小松島", "高松", 
    "防府", "広島", "玉野", "岸和田", "和歌山", "向日町", "奈良", "福井", "四日市", "松阪", 
    "豊橋", "大垣", "岐阜", "名古屋", "静岡", "伊東", "小田原", "平塚", "川崎", "松戸", 
    "立川", "京王閣", "西武園", "大宮", "宇都宮", "取手", "前橋", "富山", "弥彦", "いわき平", 
    "青森", "函館"
]

# グレードの優先順位を定義（数字が小さいほど高グレード＝上に来る）
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
    "F2": 5
}

# 日数の優先順位を定義（数字が小さいほど進行している＝上に来る）
STATUS_PRIORITY = {
    "最終日": 0,
    "4日目": 1,
    "3日目": 2,
    "2日目": 3,
    "初日": 4
}

def get_event_sort_key(event):
    """
    Pythonのsorted関数で使える並び替え用のスコア（キー）をタプルで返します。
    タプルの左側の要素ほど最優先で判定されます。
    """
    name = event.get("name", "")
    grade = event.get("grade", "-")
    status = event.get("status", "-")

    # ルール1: 玉野が絶対最優先（玉野なら0、それ以外なら1。0の方が上に来る）
    is_tamano_priority = 0 if name == "玉野" else 1

    # ルール2: グレード順（辞書にない場合は一番低い優先度にする）
    grade_score = GRADE_PRIORITY.get(grade, 99)

    # ルール3: 日程進行順（辞書にない場合は一番低い優先度にする）
    status_score = STATUS_PRIORITY.get(status, 99)

    # ルール4: 南の場から順（リストのインデックス番号を取得。ない場合は一番北にする）
    try:
        geo_score = SOUTH_TO_NORTH_TRACKS.index(name)
    except ValueError:
        geo_score = 999

    # すべてのスコアを詰め込んだタプルを返す（数字が小さい項目が上に並ぶ）
    return (is_tamano_priority, grade_score, status_score, geo_score)


def split_and_sort_events(today_merged_data):
    """
    本日のマージデータを受け取り、デイ(白枠)とナイター(青枠)に分け、
    それぞれを完璧にソートした上で、仕様書通りの『完成テキストのリスト』にして返します。
    """
    day_events = []
    night_events = []

    # 1. デイ(day)とナイター(night)に仕分ける
    for event in today_merged_data:
        if event["session"] == "day":
            day_events.append(event)
        elif event["session"] == "night":
            night_events.append(event)

    # 2. 確定した4段階の優先ルールでそれぞれを並び替える
    day_sorted = sorted(day_events, key=get_event_sort_key)
    night_sorted = sorted(night_events, key=get_event_sort_key)

    # 3. 仕様書通りの「放映用テキスト」を自動生成する
    # ※グレードと日数の間は、仕様書イメージに合わせ全角や半角2つ分のスペース「  」を確保
    day_text_list = []
    for ev in day_sorted:
        # デイは「デイ」という文字を絶対に付けない
        text = f"{ev['name']} {ev['grade']}  {ev['status']}"
        day_text_list.append(text)

    night_text_list = []
    for ev in night_sorted:
        # ナイターは場名の後ろに「ナイター」を付与
        text = f"{ev['name']}ナイター {ev['grade']}  {ev['status']}"
        night_text_list.append(text)

    # 綺麗に並び替え・整形が終わった2つのテキスト配列を返す
    return day_text_list, night_text_list
