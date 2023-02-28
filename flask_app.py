import os
from pathlib import Path
import csv
from datetime import datetime as dt
from datetime import timedelta

import peewee as pw

from dotenv import load_dotenv

load_dotenv(os.path.join(Path(__file__).parent, ".env"))

from flask import Flask, request, redirect, render_template, jsonify

from settings import CURRENT_TIMEZONE
from models import Lead, db, Call, Reminder

app = Flask(__name__)

ALLOWED_EXTENSIONS = {
    "csv",
}


@app.route("/")
def index():
    page = request.args.get("page", 1, int)
    leads = (
        Lead.filter(Lead.blacklisted == False)
        .order_by(Lead.call_count.asc())
        .paginate(page, 10)
    )

    return render_template("index.html", leads=leads, page=page)


@app.route(
    "/reject/<_id>",
    methods=[
        "POST",
    ],
)
def handle_reject(_id):
    lead: Lead = Lead.get_by_id(_id)
    Call.create(lead=lead, ended="BK")

    lead.call_count += 1
    lead.blacklisted = True
    lead.save()

    return jsonify({"success": True})


@app.route(
    "/callin2week/<_id>",
    methods=[
        "POST",
    ],
)
def callin2week(_id):
    lead: Lead = Lead.get_by_id(_id)
    Call.create(lead=lead, ended="RP")
    lead.call_count += 1
    lead.save()

    Reminder.create(
        reminded=dt.now(CURRENT_TIMEZONE) + timedelta(days=14),
        lead=lead,
        description="",
    )
    return jsonify({"success": True})


@app.route("/upload", methods=["POST", "GET"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")
    if "file" not in request.files:
        return redirect("/")
    file = request.files["file"]
    if file.filename == "":
        return redirect("/")
    if file and allowed_file(file.filename):
        filename = f"/tmp/leader{dt.now().strftime('%Y-%m-%dT%HH:%MM:%SS')}.tmp"
        file.save(filename)
        with open(filename) as stream:
            reader = csv.DictReader(
                stream,
                [
                    "name",
                    "phone",
                    "address",
                    "city",
                    "province",
                    "postal",
                    "website",
                ],
                delimiter=";",
            )

            with db.atomic():
                for lead in reader:
                    try:
                        ld = Lead.load(**lead)
                    except pw.IntegrityError:
                        pass
                    else:
                        print(ld, "ajouté")

        return redirect("/")


@app.route("/reminders", methods=["POST", "GET"])
def reminders():
    if request.method == "POST":
        lead: Lead = Lead.get_by_id(request.form.get("lead"))
        lead.call_count += 1
        lead.save()

        Call.create(lead=lead, ended="RV" if request.form.get("is_rdv") else "RP")

        Reminder.load(**request.form.to_dict())
    elif request.method == "GET":
        page = request.args.get("page", 1, int)
        remds = Reminder.filter(Reminder.is_rdv == False).paginate(page, 10)

        return render_template("reminders.html", remds=remds, page=page)

    return jsonify({"success": True})


@app.route("/calls", methods=["GET"])
def calls():
    page = request.args.get("page", 1, int)
    appels = Call.select().order_by(Call.timestamp.desc())
    return render_template("calls.html", calls=appels, page=page)


@app.route("/dashboard")
def dashboard():
    counts = {
        dt.today()
        - timedelta(days=i): Call.filter(
            Call.timestamp.day == dt.today() - timedelta(days=i)
        ).count()
        for i in range(7)
    }
    return render_template("dashboard.html", counts=counts)


def allowed_file(filename: str):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    app.run(debug=True)
