import os
from flask import Flask, request, render_template
from excel_reader import parse_excel

app = Flask(__name__)

@app.route("/")
def index():
    return "TV用パワポ自動化システム"

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        os.makedirs("uploads", exist_ok=True)

        excel = request.files["excel"]

        file_path = f"uploads/{excel.filename}"

        excel.save(file_path)

        records = parse_excel(file_path)

        return str(records[:5])

    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True)
