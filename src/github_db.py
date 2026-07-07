import os
import base64
import requests
import streamlit as st

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "tv_schedule.db"
)

# GITHUB_REPOSITORY = "X-toukou-tamano/tv-schedule-generator"
OWNER, REPO = st.secrets["GITHUB_REPOSITORY"].split("/")

TOKEN = st.secrets["GITHUB_TOKEN"]

# ブランチ固定
BRANCH = "main"

FILE_PATH = "src/tv_schedule.db"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}


def download_db():
    """
    GitHub上のDBを取得
    """

    url = (
        f"https://api.github.com/repos/"
        f"{OWNER}/{REPO}/contents/{FILE_PATH}"
        f"?ref={BRANCH}"
    )

    r = requests.get(url, headers=HEADERS)

    if r.status_code == 404:
        return False

    r.raise_for_status()

    data = r.json()

    content = base64.b64decode(data["content"])

    with open(DB_PATH, "wb") as f:
        f.write(content)

    return True


def upload_db():
    """
    GitHubへDB保存
    """

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(DB_PATH)

    with open(DB_PATH, "rb") as f:
        encoded = base64.b64encode(
            f.read()
        ).decode()

    url = (
        f"https://api.github.com/repos/"
        f"{OWNER}/{REPO}/contents/{FILE_PATH}"
    )

    sha = None

    r = requests.get(
        url,
        headers=HEADERS,
    )

    if r.status_code == 200:
        sha = r.json()["sha"]

    body = {
        "message": "Update tv_schedule.db",
        "content": encoded,
        "branch": BRANCH,
    }

    if sha:
        body["sha"] = sha

    r = requests.put(
        url,
        headers=HEADERS,
        json=body,
    )

    r.raise_for_status()

    return True
