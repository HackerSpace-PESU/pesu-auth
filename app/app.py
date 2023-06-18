import datetime
import json
import logging

import pytz
from flask import Flask, request

from pesu import PESUAcademy

app = Flask(__name__)
IST = pytz.timezone("Asia/Kolkata")

logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    format="%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(threadName)s:%(lineno)d - %(message)s",
    filemode="w",
)


@app.route("/authenticate", methods=["POST"])
def home():
    username = request.json.get("username")
    password = request.json.get("password")
    profile = request.json.get("profile", False)
    current_time = datetime.datetime.now(IST)

    # try to log in only if both username and password are provided
    if username and password:
        username = username.strip()
        password = password.strip()
        authentication_result = pesu_academy.authenticate(username, password, profile)
        authentication_result["timestamp"] = str(current_time)
        return json.dumps(authentication_result), 200

    # if either username or password is not provided, we return an error
    return json.dumps({
        "status": False,
        "message": "Username or password not provided."
    }), 400


if __name__ == "__main__":
    pesu_academy = PESUAcademy()
    app.run(host="0.0.0.0", port=5000)
