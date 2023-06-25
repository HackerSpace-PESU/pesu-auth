import datetime
import json
import logging
import os
import traceback

import gh_md_to_html
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


def convert_readme_to_html():
    html = gh_md_to_html.main("README.md").strip()
    with open("README.html", "w") as f:
        f.write(html)


@app.route("/")
def index():
    try:
        if "README.html" not in os.listdir():
            convert_readme_to_html()
        with open("README.html") as f:
            output = f.read()
            return output, 200
    except Exception as e:
        stacktrace = traceback.format_exc()
        logging.error(f"Error rendering home page: {e}: {stacktrace}")
        return "Error occurred while retrieving home page", 500


@app.route("/authenticate", methods=["POST"])
def authenticate():
    username = request.json.get("username")
    password = request.json.get("password")
    profile = request.json.get("profile", False)
    current_time = datetime.datetime.now(IST)

    # try to log in only if both username and password are provided
    if username and password:
        username = username.strip()
        password = password.strip()
        authentication_result = pesu_academy.authenticate_credentials(username, password, profile)
        authentication_result["timestamp"] = str(current_time)
        return json.dumps(authentication_result), 200

    # if either username or password is not provided, we return an error
    return json.dumps({
        "status": False,
        "message": "Username or password not provided."
    }), 400


@app.route("/authenticateManual", methods=["GET", "POST"])
def authenticate_manual():
    profile = request.json.get("profile", False)
    current_time = datetime.datetime.now(IST)
    authentication_result = pesu_academy.authenticate_manual(profile)
    authentication_result["timestamp"] = str(current_time)
    return json.dumps(authentication_result), 200


if __name__ == "__main__":
    pesu_academy = PESUAcademy()
    app.run(host="0.0.0.0", port=5000)
