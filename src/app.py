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
    get_summary,
    save_update_time,
    get_update_time
)

from keirin_json import get_race_data
from event_sorter import split_and_sort_events
from ppt_generator import parse_event_text, create_powerpoint
from download_handler import handle_pptx_download

app = Flask(__name__)
app.secret_key = "tamano-tvppt-secret-key"

create_tables()

LOGIN_ID = "tamano-keirin_TVroom"
LOGIN_PASSWORD = "tamano0401"


def get_today_sorted_data():
    """
    本日分の放映テキストリストを取得し、HTMLプレビュー用にパーツ分解した辞書配列も一緒に作成する
    """
    rows = get_events()
    today_str = datetime.date.today().isoformat()

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

    day_text_list, night_text_list = split_and_sort_events(today_merged_data)
    
    # 【追加】HTMLプレビューが絶対にバグらないよう、サーバー側でパーツをあらかじめ分解する
    preview_night = []
    for txt in night_text_list:
        n, g, s = parse_event_text(txt)
        preview_night.append({"name": n, "grade": g, "status": s})
        
    preview_day = []
    for txt in day_text_list:
        n, g, s = parse_event_text(txt)
        preview_day.append({"name": n, "grade": g, "status": s})

    return (day_text_list, night_text_list, preview_day, preview_night), today_str


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if (username == LOGIN_ID and password == LOGIN_PASSWORD):
            session["logged_in"] = True
            return redirect("/dashboard")

        return render_template("login.html", message="ログイン失敗")
    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("logged_in"):
        return redirect("/")

    message = None

    if request.method == "POST":
        os.makedirs("uploads", exist_ok=True)
        excel = request.files["excel"]
        file_path = f"uploads/{excel.filename}"
        excel.save(file_path)

        records = parse_excel(file_path)
        save_records(records)
        save_update_time()
        
        message = f"{excel.filename} を保存・更新しました"

    db_summary = get_summary()
    start_date = db_summary[0] if db_summary and db_summary[0] else None
    end_date = db_summary[1] if db_summary and db_summary[1] else None
    total_count = db_summary[2] if db_summary else 0
    last_update = get_update_time()

    (day_text_list, night_text_list, preview_day, preview_night), today_str = get_today_sorted_data()

    # ダッシュボード表示のタイミングで、裏で最新のPowerPointを生成しておく
    try:
        create_powerpoint(day_text_list, night_text_list)
    except Exception as e:
        print(f"[WARNING] 事前PPT生成失敗: {e}")

    return render_template(
        "dashboard.html",
        message=message,
        today_str=today_str,
        start_date=start_date,
        end_date=end_date,
        total_count=total_count,
        last_update=last_update,
        day_items=preview_day,       # HTML側での分解を不要にする
        night_items=preview_night    # HTML側での分解を不要にする
    )


@app.route("/events")
def events():
    if not session.get("logged_in"):
        return redirect("/")
    rows = get_events()
    return render_template("events.html", rows=rows)


@app.route("/download")
def download_powerpoint():
    (day_text_list, night_text_list, _, _), _ = get_today_sorted_data()
    return handle_pptx_download(session, day_text_list, night_text_list)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
