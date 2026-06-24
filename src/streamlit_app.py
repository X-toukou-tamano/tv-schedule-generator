import streamlit as st

from database import (
    get_summary,
    get_update_time,
)

USERNAME = "tamano-keirin_TVroom"
PASSWORD = "tamano0401"

st.set_page_config(
    page_title="TV放映予定管理",
    layout="wide"
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
