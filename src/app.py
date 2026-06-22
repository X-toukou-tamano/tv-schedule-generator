import os
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    session
)

from excel_reader import parse_excel
from database import (
    create_tables,
    save_records,
    get_events
)

app = Flask(__name__)
app.secret_key = "tamano-tvppt-secret-key"

create_tables()

LOGIN_ID = "tamano-keirin_TVroom"
LOGIN_PASSWORD = "tamano0401"


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if (
            username == LOGIN_ID and
            password == LOGIN_PASSWORD
        ):
            session["logged_in"] = True

            return redirect("/upload")

        return render_template(
            "login.html",
            message="ログイン失敗"
        )

    return render_template("login.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():

    if not session.get("logged_in"):
        return redirect("/")

    if request.method == "POST":

        os.makedirs(
            "uploads",
            exist_ok=True
        )

        excel = request.files["excel"]

        file_path = (
            f"uploads/{excel.filename}"
        )

        excel.save(file_path)

        records = parse_excel(file_path)

        save_records(records)

        return render_template(
            "upload.html",
            message=f"{excel.filename} を保存しました",
            count=len(records),
            records=records[:20]
        )

    return render_template("upload.html")


@app.route("/events")
def events():

    if not session.get("logged_in"):
        return redirect("/")

    rows = get_events()

    return render_template(
        "events.html",
        rows=rows
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
