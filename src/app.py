from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "TV用パワポ自動化システム"

@app.route("/upload")
def upload():
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
