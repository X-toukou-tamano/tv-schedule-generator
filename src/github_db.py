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

# GitHub上で保存する場所
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
    """
    GitHub上のDBファイルのSHAを取得

    Returns
    -------
    str | None
        存在すればSHA
        無ければNone
    """

    response = requests.get(
        API_URL,
        headers=HEADERS,
        params={
            "ref": BRANCH
        },
        timeout=30,
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()

    return response.json()["sha"]


# =====================================================
# GitHub → ローカル
# =====================================================

def download_db():
    """
    GitHubからSQLiteを取得

    Returns
    -------
    bool
        True : ダウンロード成功
        False : GitHubに存在しない
    """

    print("[GitHub] DBダウンロード開始")

    response = requests.get(
        API_URL,
        headers=HEADERS,
        params={
            "ref": BRANCH
        },
        timeout=30,
    )

    if response.status_code == 404:
        print("[GitHub] DBなし（初回起動）")
        return False

    response.raise_for_status()

    content = base64.b64decode(
        response.json()["content"]
    )

    with open(DB_PATH, "wb") as f:
        f.write(content)

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
        encoded = base64.b64encode(
            f.read()
        ).decode()

    sha = get_db_sha()

    body = {
        "message": "Update tv_schedule.db",
        "content": encoded,
        "branch": BRANCH,
    }

    if sha:
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

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"GitHub保存失敗\n"
            f"status={response.status_code}\n"
            f"{response.text}"
        )

    print("[GitHub] 保存成功")

    return True


# =====================================================
# GitHub上にDBが存在するか
# =====================================================

def exists_db():
    """
    GitHub上にDBが存在するか

    Returns
    -------
    bool
    """

    return get_db_sha() is not None
