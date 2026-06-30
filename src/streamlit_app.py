import os
from datetime import datetime
import streamlit as st

from database import (
    create_tables,
    get_generate_history,
    get_summary,
    get_update_time,
    save_generate_history,
    save_records,
    save_update_time,
)
from excel_reader import get_upload_info, parse_excel
from ppt_service import generate_all_ppt, generate_range_ppt
from schedule_updater import update_schedule_info

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
    pw = st.text_input("パスワード", type="password")

    if st.button("ログイン"):
        if user == USERNAME and pw == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("IDまたはパスワードが違います")
    st.stop()

# ----------------------------
# ダッシュボード
# ----------------------------
st.title("TV放映予定管理システム")

db_start_date, db_end_date, total_count = get_summary()
last_update = get_update_time()

# 履歴の初期取得
range_from, range_to = get_generate_history("range")
batch_from, batch_to = get_generate_history("batch")

st.success("ログイン成功")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("登録件数", f"{total_count}件")

with col2:
    st.metric("開始日", db_start_date if db_start_date else "-")

with col3:
    st.metric("終了日", db_end_date if db_end_date else "-")

st.write("")

# 各種履歴情報エリア
hist_col1, hist_col2 = st.columns(2)
with hist_col1:
    st.subheader("最終更新日時")
    st.info(last_update if last_update else "未更新")

with hist_col2:
    st.subheader("前回パワーポイント生成履歴")
    # 書き換え用のプレースホルダー
    history_placeholder = st.empty()


# 履歴描画用の共通関数
def render_history_info(placeholder, r_from, r_to, b_from, b_to):
    if not r_from and not b_from:
        placeholder.info("生成履歴なし")
    else:
        md_text = ""
        if r_from and r_to:
            md_text += f"**指定期間生成**\n{r_from} ～ {r_to}\n\n"
        if b_from and b_to:
            md_text += f"**公開全期間生成**\n{b_from} ～ {b_to}\n\n"
        placeholder.markdown(md_text)


# 初回読み込み時の履歴描画
render_history_info(
    history_placeholder,
    range_from,
    range_to,
    batch_from,
    batch_to,
)

st.divider()

# ----------------------------
# Excelアップロード
# ----------------------------
st.subheader("Excelアップロード")

uploaded_file = st.file_uploader("開催カレンダーExcel", type=["xlsx", "xlsm"])

if uploaded_file is not None:
    if st.button("DB更新"):
        try:
            os.makedirs("excel_data", exist_ok=True)
            temp_name = os.path.join("excel_data", uploaded_file.name)

            with open(temp_name, "wb") as f:
                f.write(uploaded_file.getbuffer())

            year, term = get_upload_info(temp_name)
            filename = f"{year}_{term}.xlsx"
            save_path = os.path.join("excel_data", filename)

            os.replace(temp_name, save_path)
            records = parse_excel(save_path)

            save_records(records)
            count = update_schedule_info()
            save_update_time()

            st.success(
                f"{len(records)}件登録しました\n"
                f"{count}件 開催情報を更新しました"
            )
            st.rerun()

        except Exception as e:
            st.exception(e)

# ----------------------------
# パワーポイント生成エリア
# ----------------------------
st.divider()
st.subheader("PowerPoint生成")

col1, col2 = st.columns(2)
with col1:
    selected_start = st.date_input(
        "開始日",
        value=datetime.fromisoformat(db_start_date).date() if db_start_date else datetime.today().date(),
    )

with col2:
    selected_end = st.date_input(
        "終了日",
        value=datetime.fromisoformat(db_end_date).date() if db_end_date else datetime.today().date(),
    )

if st.button("指定期間を生成", use_container_width=True):
    if selected_start > selected_end:
        st.error("開始日が終了日より後になっています。")
    else:
        try:
            zip_data = generate_range_ppt(
                selected_start,
                selected_end,
            )

            if zip_data is None:
                st.session_state["zip_data"] = None
                st.session_state["success_msg"] = None
                st.warning("指定期間に生成できるデータがありません。")
            else:
                st.session_state["zip_data"] = zip_data
                st.session_state["success_msg"] = (
                    f"{selected_start} ～ {selected_end} を生成しました。"
                )

                # DBに履歴を保存
                save_generate_history(
                    "range",
                    selected_start,
                    selected_end,
                )

                # 即時書き換え
                range_from, range_to = get_generate_history("range")
                render_history_info(
                    history_placeholder,
                    range_from,
                    range_to,
                    batch_from,
                    batch_to,
                )

        except Exception as e:
            st.error(
                f"パワーポイント生成中にエラーが発生しました: {e}"
            )

if st.button("公開済み全期間を生成", use_container_width=True):
    try:
        result = generate_all_ppt()

        if not result:
            st.session_state["zip_data"] = None
            st.session_state["success_msg"] = None
            st.warning("生成できるデータがありません。")
        else:
            zip_data, last_date = result

            if zip_data is None:
                st.session_state["zip_data"] = None
                st.session_state["success_msg"] = None
                st.warning("生成できるデータがありません。")
            else:
                st.session_state["zip_data"] = zip_data
                st.session_state["success_msg"] = (
                    f"{db_start_date} ～ {last_date} を生成しました。"
                )

                # DBに履歴を保存
                save_generate_history("batch", db_start_date, last_date)

                # 即時書き換え
                batch_from, batch_to = get_generate_history("batch")
                render_history_info(
                    history_placeholder,
                    range_from,
                    range_to,
                    batch_from,
                    batch_to,
                )
    except Exception as e:
        st.error(f"パワーポイント一括生成中にエラーが発生しました: {e}")

# --- ダウンロードボタンの表示エリア ---
if st.session_state.get("zip_data"):
    success_msg = st.session_state.get(
        "success_msg",
        "パワーポイントの生成が完了しました。"
    )
    st.success(success_msg)

    st.download_button(
        label="ZIPダウンロード",
        data=st.session_state["zip_data"],
        file_name="場内放映予定.zip",
        mime="application/zip",
        use_container_width=True,
        key="download_zip",
    )

st.divider()
