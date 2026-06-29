import streamlit as st

from database import (
    create_tables,
    get_summary,
    get_update_time,
    save_records,
    save_update_time,
    save_generate_history,
    get_generate_history,
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
import os
st.error(os.path.abspath("tv_schedule.db"))

# DB初期化
create_tables()
st.error("create_tables() 実行")

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

# 履歴の初期取得
range_from, range_to = get_generate_history("range")
batch_from, batch_to = get_generate_history("batch")

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

# 各種履歴情報エリア
hist_col1, hist_col2 = st.columns(2)

with hist_col1:
    st.subheader("最終更新日時")
    st.info(
        last_update if last_update else "未更新"
    )

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
# パワーポイント生成エリア
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
        try:
            zip_path = generate_range_ppt(
                selected_start,
                selected_end,
            )

            if zip_path is None:
                st.session_state["zip_path"] = None
                st.session_state["success_msg"] = None
                st.warning(
                    "指定期間に生成できるデータがありません。"
                )
            else:
                st.session_state["zip_path"] = zip_path
                st.session_state["success_msg"] = f"{selected_start} ～ {selected_end} を生成しました。"
                
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
            # 前回成功時のダウンロードリンク情報を巻き添えで消さないよう、セッション状態は維持
            st.error(f"パワーポイント生成中にエラーが発生しました: {e}")


if st.button(
    "公開済み全期間を生成",
    use_container_width=True,
):

    try:
        # 戻り値の不整合（Noneや空リストなど）を安全に防ぐ堅牢な実装
        result = generate_all_ppt()

        if not result:
            st.session_state["zip_path"] = None
            st.session_state["success_msg"] = None
            st.warning(
                "生成できるデータがありません。"
            )
        else:
            zip_path, last_date = result
            if zip_path is None:
                st.session_state["zip_path"] = None
                st.session_state["success_msg"] = None
                st.warning(
                    "生成できるデータがありません。"
                )
            else:
                st.session_state["zip_path"] = zip_path
                st.session_state["success_msg"] = f"{db_start_date} ～ {last_date} を生成しました。"
                
                # DBに履歴を保存
                save_generate_history(
                    "batch",
                    db_start_date,
                    last_date,
                )
                
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
        # 前回成功時のダウンロードリンク情報を巻き添えで消さないよう、セッション状態は維持
        st.error(f"パワーポイント一括生成中にエラーが発生しました: {e}")


# --- ダウンロードボタンの表示エリア ---
if (
    "zip_path" in st.session_state 
    and st.session_state["zip_path"] is not None
    and "success_msg" in st.session_state
):
    zip_path = st.session_state["zip_path"]
    
    # 物理的なファイルの存在チェック
    if os.path.exists(zip_path):
        st.success(st.session_state["success_msg"])
        
        with open(zip_path, "rb") as f:
            st.download_button(
                label="ZIPダウンロード",
                data=f,
                file_name=os.path.basename(zip_path),
                mime="application/zip",
                use_container_width=True,
            )
    else:
        st.warning("ZIPファイルが見つかりません。再生成してください。")
        # 古くなった無効なパス情報をクリア
        st.session_state["zip_path"] = None
        st.session_state["success_msg"] = None

st.divider()
