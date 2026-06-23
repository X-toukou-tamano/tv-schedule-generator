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
    get_events,
    get_summary  # ← 追加
)

from keirin_json import get_race_data
from event_sorter import split_and_sort_events

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

    # Excelファイルがアップロードされた場合
    if request.method == "POST":
        os.makedirs("uploads", exist_ok=True)
        excel = request.files["excel"]
        file_path = f"uploads/{excel.filename}"
        excel.save(file_path)

        # Excelを解析してDBに保存（上書き処理）
        records = parse_excel(file_path)
        save_records(records)
        message = f"{excel.filename} を保存・更新しました"

    # --- 以下、常にダッシュボードで表示するためのデータ作成処理 ---

    # 1. DBからExcelデータの登録期間（サマリー）を取得
    # summary は (MIN(date), MAX(date), COUNT(*)) のタプル形式
    db_summary = get_summary()
    start_date = db_summary[0] if db_summary and db_summary[0] else None
    end_date = db_summary[1] if db_summary and db_summary[1] else None
    total_count = db_summary[2] if db_summary else 0

    # 2. database.py から本日開催スケジュールを照合するために全件取得
    rows = get_events()
    today_str = datetime.date.today().isoformat()

    # 3. keirin_json.py から公式JSONを取得して本日分をマージ
    vinfo_map = {}
    try:
        race_data = get_race_data()
        if race_data and "RaceList" in race_data:
            for info in race_data["RaceList"]:
                vname = info.get("keirinjoName")
                if vname:
                    vinfo_map[vname] = info
    except Exception as e:
        print(f"[WARNING] 公式JSONの読み込みに失敗しました: {e}")

    today_merged_data = []
    for row in rows:
        event_date = row[0]
        venue_name = row[1]

        if event_date == today_str and venue_name in vinfo_map:
            info = vinfo_map[venue_name]
            kubun_code = str(info.get("kubunIconName", "")).strip()

            session_type = None
            if kubun_code == "1":
                session_type = "day"
            elif kubun_code == "3":
                session_type = "night"
            else:
                continue

            status_text = info.get("nichijiIconName", "-")
            grade_text = info.get("gradeIconName", "-")

            today_merged_data.append({
                "name": venue_name,
                "session": session_type,
                "grade": grade_text,
                "status": status_text
            })

    # 4. 並び替え・仕分けの実行
    day_text_list, night_text_list = split_and_sort_events(today_merged_data)

    return render_template(
        "dashboard.html",
        message=message,
        today_str=today_str,
        start_date=start_date,
        end_date=end_date,
        total_count=total_count,
        day_text_list=day_text_list,
        night_text_list=night_text_list
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
