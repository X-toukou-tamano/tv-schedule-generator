import io
import streamlit as st
from github import Github
from github.GithubException import UnknownObjectException

# ----------------------------
# GitHub接続
# ----------------------------

REPO_NAME = st.secrets["GITHUB_REPOSITORY"]

TOKEN = st.secrets["GITHUB_TOKEN"]

FOLDER = "excel_data"


def get_repo():
    g = Github(TOKEN)
    return g.get_repo(REPO_NAME)


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
    filename
):

    repo = get_repo()

    path = f"{FOLDER}/{filename}"

    print(f"===== upload_excel =====")
    print(f"path = {path}")

    try:

        old = repo.get_contents(path)

        print("UPDATE MODE")
        print(f"sha = {old.sha}")

        result = repo.update_file(
            path=path,
            message=f"Update {filename}",
            content=file_bytes,
            sha=old.sha
        )

        print(result)

    except Exception as e:

        print("CREATE MODE")
        print(type(e))
        print(e)

        result = repo.create_file(
            path=path,
            message=f"Create {filename}",
            content=file_bytes
        )

        print(result)

# ----------------------------
# Excelダウンロード
# ----------------------------

def download_excel(filename):

    repo = get_repo()

    path = f"{FOLDER}/{filename}"

    file = repo.get_contents(path)

    return io.BytesIO(file.decoded_content)


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
