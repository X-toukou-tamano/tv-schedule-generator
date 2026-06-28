import io
import streamlit as st
from github import Github
from github.GithubException import UnknownObjectException

# ----------------------------
# GitHub接続
# ----------------------------

FOLDER = "excel_data"


def get_repo():
    """
    Secretsはimport時ではなく、
    実際にGitHubへアクセスする時だけ取得する。
    """

    try:

        repo_name = st.secrets["GITHUB_REPOSITORY"]

        token = st.secrets["GITHUB_TOKEN"]

    except Exception as e:

        raise RuntimeError(
            "GitHub Secrets が設定されていません。"
        ) from e

    g = Github(token)

    return g.get_repo(repo_name)


# ----------------------------
# 保存済みExcel一覧取得
# ----------------------------

def list_excels():

    repo = get_repo()

    try:

        files = repo.get_contents(FOLDER)

    except UnknownObjectException:

        return []

    return sorted(
        [
            f.name
            for f in files
            if f.name.endswith(".xlsx")
        ]
    )


# ----------------------------
# Excelアップロード
# ----------------------------

def upload_excel(
    file_bytes,
    filename,
):

    repo = get_repo()

    path = f"{FOLDER}/{filename}"

    try:

        old = repo.get_contents(path)

        repo.update_file(
            path=path,
            message=f"Update {filename}",
            content=file_bytes,
            sha=old.sha,
        )

    except UnknownObjectException:

        repo.create_file(
            path=path,
            message=f"Create {filename}",
            content=file_bytes,
        )


# ----------------------------
# Excelダウンロード
# ----------------------------

def download_excel(filename):

    repo = get_repo()

    path = f"{FOLDER}/{filename}"

    file = repo.get_contents(path)

    return io.BytesIO(
        file.decoded_content
    )


# ----------------------------
# Excel存在確認
# ----------------------------

def exists(filename):

    repo = get_repo()

    path = f"{FOLDER}/{filename}"

    try:

        repo.get_contents(path)

        return True

    except UnknownObjectException:

        return False
