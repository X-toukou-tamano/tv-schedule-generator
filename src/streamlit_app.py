import streamlit as st

USERNAME = "tamano-keirin_TVroom"
PASSWORD = "tamano0401"

st.set_page_config(
    page_title="TV放映予定管理",
    layout="wide"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("TV放映予定管理")

    user = st.text_input("ID")
    pw = st.text_input("パスワード", type="password")

    if st.button("ログイン"):
        if user == USERNAME and pw == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("IDまたはパスワードが違います")

    st.stop()

st.title("TV放映予定管理システム")

st.success("ログイン成功")
