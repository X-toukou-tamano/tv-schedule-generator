import streamlit as st

from database import (
    create_tables,
    get_summary,
    get_update_time,
    save_records,
    save_update_time,
)

from excel_reader import (
    parse_excel,
    get_upload_info,
)

from today_service import get_today_sorted_data

from github_storage import (
    upload_excel,
    download_excel,
    list_excels,
)

import os

USERNAME = "tamano-keirin_TVroom"
PASSWORD = "tamano0401"

st.set_page_config(
    page_title="TV放映予定管理",
    layout="wide"
)

# DB初期化
create_tables()

from datetime import datetime
from zoneinfo import ZoneInfo
import tempfile

summary = get_summary()

if summary[2] == 0:

    today = datetime.now(
        ZoneInfo("Asia/Tokyo")
    ).date()

    if 4 <= today.month <= 9:
        term = "上期"
        reiwa = today.year - 2018
    else:
        term = "下期"
        reiwa = today.year - 2019

    filename = f"R{reiwa}_{term}.xlsx"

    try:

        excel = download_excel(filename)

        with tempfile.NamedTemporaryFile(
            suffix=".xlsx",
            delete=False
        ) as tmp:

            tmp.write(excel.read())
            temp_path = tmp.name

        records = parse_excel(
            temp_path
        )

        save_records(records)

    except Exception:
        pass

# ----------------------------
# ログイン状態管理
# ----------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ----------------------------
# ログイン画面
# ----------------------------

if not st.session_state.logged_in:

    st.title("TV放映予定管理")

    user = st.text_input("ID")
    pw = st.text_input(
        "パスワード",
        type="password"
    )

    if st.button("ログイン"):

        if (
            user == USERNAME
            and pw == PASSWORD
        ):
            st.session_state.logged_in = True
            st.rerun()

        else:
            st.error(
                "IDまたはパスワードが違います"
            )

    st.stop()
# ----------------------------
# ダッシュボード
# ----------------------------

st.title("TV放映予定管理システム")

summary = get_summary()
last_update = get_update_time()

start_date = summary[0]
end_date = summary[1]
total_count = summary[2]

st.success("ログイン成功")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "登録件数",
        f"{total_count}件"
    )

with col2:
    st.metric(
        "開始日",
        start_date if start_date else "-"
    )

with col3:
    st.metric(
        "終了日",
        end_date if end_date else "-"
    )

st.write("")

st.subheader("最終更新日時")

st.info(
    last_update if last_update else "未更新"
)

st.divider()

st.subheader("Excelアップロード")

uploaded_file = st.file_uploader(
    "開催カレンダーExcel",
    type=["xlsx", "xlsm"]
)

if uploaded_file is not None:

    if st.button("DB更新"):

        os.makedirs(
            UPLOAD_DIR,
            exist_ok=True
        )

        temp_path = os.path.join(
            UPLOAD_DIR,
            uploaded_file.name
        )

        with open(
            temp_path,
            "wb"
        ) as f:
            f.write(
                uploaded_file.getbuffer()
            )

        year, term = get_upload_info(
            temp_path
        )

        filename = f"{year}_{term}.xlsx"

        upload_excel(
            uploaded_file.getvalue(),
            filename
        )

        records = parse_excel(
            temp_path
        )

        save_records(
            records
        )

        save_update_time()

        st.success(
            f"{len(records)}件登録しました"
        )

        st.rerun()
# ----------------------------
# 仮表示エリア
# ----------------------------

st.divider()

st.subheader("本日開催")

(
    (
        day_events,
        night_events,
        preview_day,
        preview_night,
    ),
    today_str,
) = get_today_sorted_data()

st.caption(
    f"対象日: {today_str}"
)

col1, col2 = st.columns(2)

with col1:

    st.markdown("### デイ")

    if preview_day:

        for item in preview_day:

            st.write(
                f"{item['name']} "
                f"{item['grade']} "
                f"{item['status']}"
            )

    else:

        st.info("開催なし")

with col2:

    st.markdown("### ナイター")

    if preview_night:

        for item in preview_night:

            st.write(
                f"{item['name']} "
                f"{item['grade']} "
                f"{item['status']}"
            )

    else:

        st.info("開催なし")

st.divider()

st.subheader("PowerPoint")

if st.button("PPT生成"):

    from ppt_generator import create_powerpoint

    output_path = create_powerpoint(
        day_events,
        night_events
    )

    st.success(
        "PowerPoint生成完了"
    )

    with open(
        output_path,
        "rb"
    ) as f:

        st.download_button(
            label="PPTダウンロード",
            data=f,
            file_name=os.path.basename(output_path),
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
