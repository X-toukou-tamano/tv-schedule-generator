import os
import datetime
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    session
)

from excel_reader import parse_excel
from database import (
    create_tables,
    save_records,
    get_events
)

# JSON取得用の別のpyファイルから関数をインポート
# ※ファイル名が異なる場合は、実際のファイル名に合わせて書き換えてください。
from fetch_api import get_race_data

app = Flask(__name__)
app.secret_key = "tamano-tvppt-secret-key"

create_tables()

LOGIN_ID = "tamano-keirin_TVroom"
LOGIN_PASSWORD = "tamano0401"


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if (
            username == LOGIN_ID and
            password == LOGIN_PASSWORD
        ):
            session["logged_in"] = True
            return redirect("/dashboard")

        return render_template(
            "login.html",
            message="ログイン失敗"
        )

    return render_template(
        "login.html"
    )


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("logged_in"):
        return redirect("/")

    message = None

    if request.method == "POST":
        os.makedirs(
            "uploads",
            exist_ok=True
        )

        excel = request.files["excel"]

        file_path = (
            f"uploads/{excel.filename}"
        )

        excel.save(file_path)

        records = parse_excel(file_path)
        save_records(records)

        message = (
            f"{excel.filename} を保存しました"
        )

    return render_template(
        "dashboard.html",
        message=message
    )


@app.route("/events")
def events():
    if not session.get("logged_in"):
        return redirect("/")

    # 1. database.py から全日程スケジュールを取得
    rows = get_events()

    # YYYY-MM-DD形式の「本日」の日付文字列を取得
    today_str = datetime.date.today().isoformat()
    # テスト検証用（JSONの日付 "20260623" と比較するために YYYYMMDD 形式も用意）
    today_nodash = datetime.date.today().strftime("%Y%mdd")

    # 2. 別のpyファイルの get_race_data() から本日のJSON公式データを取得してマップ化
    vinfo_map = {}
    try:
        race_data = get_race_data()
        # 生のJSON構造に合わせて "RaceList" から抽出
        if race_data and "RaceList" in race_data:
            for info in race_data["RaceList"]:
                vname = info.get("keirinjoName")  # 生のJSONキー「keirinjoName」
                if vname:
                    vinfo_map[vname] = info
    except Exception as e:
        print(f"[WARNING] 公式JSONの読み込みに失敗しました: {e}")

    # 3. 本日開催のデータを仕様書通り1つのデータオブジェクトとして記憶・整理する
    today_merged_data = []

    for row in rows:
        event_date = row[0]   # DBの日付文字列 (YYYY-MM-DD)
        venue_name = row[1]   # DBの場名文字列 (例: "小田原", "久留米")

        # 「本日開催」の場だけを抽出対象とする
        if event_date == today_str and venue_name in vinfo_map:
            info = vinfo_map[venue_name]
            kubun_code = str(info.get("kubunIconName", "")).strip()

            # 本物の数字ルールで区分判定 ＆ モーニング("8")・ミッドナイト("5")の除外処理
            session_type = None
            if kubun_code == "1":
                session_type = "day"
            elif kubun_code == "3":
                session_type = "night"
            else:
                # 5(ミッドナイト), 8(モーニング) またはそれ以外なら記憶せずスキップ
                continue

            # 日数テキストはJSONの「nichijiIconName」に入っている綺麗な文字をそのまま拝借
            status_text = info.get("nichijiIconName", "-")

            # グレードはJSONの「gradeIconName」をそのまま使用
            grade_text = info.get("gradeIconName", "-")

            # 仕様書通りの4つの項目（name, session, grade, status）を1つの塊として記憶させる
            today_merged_data.append({
                "name": venue_name,
                "session": session_type,
                "grade": grade_text,
                "status": status_text
            })

    # デバッグ確認用（記憶されたデータをターミナルで綺麗に見られます）
    print("\n========================================")
    print("【内部記憶データ】本日分マージ結果（モーニング・ミッド除外版）:")
    import json
    print(json.dumps(today_merged_data, indent=2, ensure_ascii=False))
    print("========================================\n")

    # 既存の一覧表示画面の表示を維持して返す
    return render_template(
        "events.html",
        rows=rows
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
