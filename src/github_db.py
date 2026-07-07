import os
import base64
import requests
import streamlit as st

# =====================================================
# 設定
# =====================================================

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "tv_schedule.db"
)

OWNER, REPO = st.secrets["GITHUB_REPOSITORY"].split("/")

TOKEN = st.secrets["GITHUB_TOKEN"]

BRANCH = "main"

FILE_PATH = "tv_schedule.db"

API_URL = (
    f"https://api.github.com/repos/"
    f"{OWNER}/{REPO}/contents/{FILE_PATH}"
)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}


# =====================================================
# GitHub上のSHA取得
# =====================================================

def get_db_sha():
    """GitHub上のDBファイルのSHAを取得"""

    response = requests.get(
        API_URL,
        headers=HEADERS,
        params={"ref": BRANCH},
        timeout=30,
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()

    return response.json()["sha"]


# =====================================================
# GitHub上にDBが存在するか
# =====================================================

def exists_db():
    """GitHub上にDBが存在するか"""

    return get_db_sha() is not None


# =====================================================
# GitHub → ローカル
# =====================================================

def download_db(force=False):
    """
    GitHubからSQLiteを取得

    Parameters
    ----------
    force : bool
        TrueならローカルDBがあっても上書きする

    Returns
    -------
    bool
    """

    if os.path.exists(DB_PATH) and not force:
        print("[GitHub] ローカルDBを使用")
        return True

    print("[GitHub] DBダウンロード開始")

    response = requests.get(
        API_URL,
        headers=HEADERS,
        params={"ref": BRANCH},
        timeout=30,
    )

    if response.status_code == 404:
        print("[GitHub] DBなし（初回起動）")
        return False

    response.raise_for_status()

    content = response.json()["content"].replace("\n", "")

    with open(DB_PATH, "wb") as f:
        f.write(base64.b64decode(content))

    print("[GitHub] DBダウンロード成功")

    return True


# =====================================================
# ローカル → GitHub
# =====================================================

def upload_db():
    """
    SQLiteをGitHubへ保存
    """

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(DB_PATH)

    print("[GitHub] DBアップロード開始")

    with open(DB_PATH, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    body = {
        "message": "Update tv_schedule.db",
        "content": encoded,
        "branch": BRANCH,
    }

    sha = get_db_sha()

    if sha is not None:
        body["sha"] = sha
        print("[GitHub] 上書き保存")
    else:
        print("[GitHub] 新規保存")

    response = requests.put(
        API_URL,
        headers=HEADERS,
        json=body,
        timeout=60,
    )

    response.raise_for_status()

    print("[GitHub] 保存成功")

    return True
