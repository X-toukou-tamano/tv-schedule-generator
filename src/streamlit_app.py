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

from github_storage import (
    upload_excel,
    download_excel,
    list_excels,
)
from schedule_updater import update_schedule_info
from ppt_service import (
    generate_range_ppt,
    generate_all_ppt,
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

    target = f"R{reiwa}_{term}"

    files = list_excels()

    filename = next(
        (
            f
            for f in files
            if f.startswith(target)
        ),
        None
    )

    if filename is not None:

        try:

            excel = download_excel(
                filename
            )

            with tempfile.NamedTemporaryFile(
                suffix=".xlsx",
                delete=False
            ) as tmp:

                tmp.write(
                    excel.read()
                )

                temp_path = tmp.name

            records = parse_excel(temp_path)

            save_records(records)

            update_schedule_info()

            save_update_time()

        except Exception as e:

            st.error(
                f"Excel読込エラー: {e}"
            )

    else:

        st.warning(
            f"{target} のExcelが見つかりません。"
        )

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

db_start_date = summary[0]
db_end_date = summary[1]
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
        db_start_date if db_start_date else "-"
    )

with col3:
    st.metric(
        "終了日",
        db_end_date if db_end_date else "-"
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

        temp_dir = tempfile.gettempdir()

        temp_path = os.path.join(
            temp_dir,
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

        save_records(records)

        count = update_schedule_info()

        save_update_time()

        st.success(
            f"{len(records)}件登録しました\n"
            f"{count}件 開催情報を更新しました"
        )

        st.rerun()

# ----------------------------
# 仮表示エリア
# ----------------------------

st.divider()

st.subheader("PowerPoint生成")

col1, col2 = st.columns(2)

with col1:

    selected_start = st.date_input(
        "開始日",
        value=datetime.fromisoformat(db_start_date).date()
        if db_start_date else datetime.today().date(),
    )

with col2:

    selected_end = st.date_input(
        "終了日",
        value=datetime.fromisoformat(db_end_date).date()
        if db_end_date else datetime.today().date(),
    )

if st.button(
    "指定期間を生成",
    use_container_width=True,
):

    if selected_start > selected_end:
        st.error("開始日が終了日より後になっています。")
    else:
        zip_path = generate_range_ppt(
            selected_start,
            selected_end,
        )

        if zip_path is None:
            # 古いZIP情報を確実にクリア
            st.session_state["zip_path"] = None
            st.session_state["success_msg"] = None
            st.warning(
                "指定期間に生成できるデータがありません。"
            )
        else:
            # session_stateに保存
            st.session_state["zip_path"] = zip_path
            st.session_state["success_msg"] = f"{selected_start} ～ {selected_end} を生成しました。"


if st.button(
    "公開済み全期間を生成",
    use_container_width=True,
):

    zip_path, last_date = generate_all_ppt()

    if zip_path is None:
        # 古いZIP情報を確実にクリア
        st.session_state["zip_path"] = None
        st.session_state["success_msg"] = None
        st.warning(
            "生成できるデータがありません。"
        )
    else:
        # session_stateに保存
        st.session_state["zip_path"] = zip_path
        st.session_state["success_msg"] = f"{db_start_date} ～ {last_date} を生成しました。"


# --- ダウンロードボタンの表示エリア ---
if (
    "zip_path" in st.session_state 
    and st.session_state["zip_path"] is not None
    and "success_msg" in st.session_state
):
    
    st.success(st.session_state["success_msg"])
    
    with open(
        st.session_state["zip_path"],
        "rb",
    ) as f:

        st.download_button(
            label="ZIPダウンロード",
            data=f,
            file_name=os.path.basename(st.session_state["zip_path"]),
            mime="application/zip",
            use_container_width=True,
        )

st.divider()
