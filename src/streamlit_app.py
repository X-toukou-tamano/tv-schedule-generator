import streamlit as st

from database import (
    create_tables,
    get_summary,
    get_update_time,
    save_records,
    save_update_time,
)

from excel_reader import parse_excel

import tempfile
import os

USERNAME = "tamano-keirin_TVroom"
PASSWORD = "tamano0401"

st.set_page_config(
    page_title="TV放映予定管理",
    layout="wide"
)

# DB初期化
create_tables()

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

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".xlsx"
        ) as tmp:

            tmp.write(
                uploaded_file.getbuffer()
            )

            temp_path = tmp.name

        try:

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

        finally:

            if os.path.exists(
                temp_path
            ):
                os.remove(
                    temp_path
                )

# ----------------------------
# 仮表示エリア
# ----------------------------

st.divider()

st.subheader("本日開催")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### デイ")
    st.info("次工程で実装")

with col2:
    st.markdown("### ナイター")
    st.info("次工程で実装")
