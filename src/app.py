import os
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def index():
    return "TV用パワポ自動化システム"

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        os.makedirs("uploads", exist_ok=True)

        excel = request.files["excel"]

        excel.save(
            f"uploads/{excel.filename}"
        )

        return f"{excel.filename} を保存しました"

    return """
    <h1>Excelアップロード</h1>

    <form method="post" enctype="multipart/form-data">
        <input type="file" name="excel">
        <button type="submit">
            アップロード
        </button>
    </form>
    """

if __name__ == "__main__":
    app.run(debug=True)
