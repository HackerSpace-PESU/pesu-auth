import pytz
import json
import datetime
from flask import Flask, request
from .utils import *


app = Flask(__name__)
IST = pytz.timezone("Asia/Kolkata")


@app.route("/", methods=["POST"])
def home():
    username = request.form.get("username")
    password = request.form.get("password")
    get_profile_data = str(request.form.get("get_profile_data")).lower() == "true"

    login_status = False
    profile_data = dict()
    if username != None and password != None:
        login_status, profile_data = authenticatePESU(username, password, get_profile_data)

    result = {
        "authentication-status": login_status,
        "timestamp": str(datetime.datetime.now(IST)),
    }

    if get_profile_data:
        result["profile-data"] = profile_data

    result = json.dumps(result)
    return result, 200


if __name__ == "__main__":
    app.run()
