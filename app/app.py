import datetime
import json
import logging
import os
import re
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
    """
    Convert the README.md file to HTML and save it as README.html so that it can be rendered on the home page.
    """
    readme_content = open("README.md").read().strip()
    readme_content = re.sub(r":\w+: ", "", readme_content)
    with open("README_tmp.md", "w") as f:
        f.write(readme_content)
    html = gh_md_to_html.main("README_tmp.md").strip()
    with open("README.html", "w") as f:
        f.write(html)


def validate_input(
    username: str,
    password: str,
    profile: bool,
    know_your_class_and_section: bool,
    fields: list[str],
):
    """
    Validate the input provided by the user.
    :param username: str: The username of the user.
    :param password: str: The password of the user.
    :param profile: bool: Whether to fetch the profile details of the user.
    :param know_your_class_and_section: bool: Whether to fetch the class and section details of the user.
    :param fields: dict: The fields to fetch from the user's profile.
    """
    assert username is not None, "Username not provided."
    assert isinstance(username, str), "Username should be a string."
    assert password is not None, "Password not provided."
    assert isinstance(password, str), "Password should be a string."
    assert isinstance(profile, bool), "Profile should be a boolean."
    assert isinstance(
        know_your_class_and_section, bool
    ), "know_your_class_and_section should be a boolean."
    assert fields is None or (
        isinstance(fields, list) and fields
    ), "Fields should be a non-empty list or None."
    if fields is not None:
        for field in fields:
            assert (
                isinstance(field, str) and field in pesu_academy.DEFAULT_FIELDS
            ), f"Invalid field: '{field}'. Valid fields are: {pesu_academy.DEFAULT_FIELDS}."


@app.route("/")
def index():
    """
    Render the home page with the README.md content.
    """
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
    """
    Authenticate the user with the provided username and password.
    """
    # Extract the input provided by the user
    current_time = datetime.datetime.now(IST)
    username = request.json.get("username")
    password = request.json.get("password")
    profile = request.json.get("profile", False)
    know_your_class_and_section = request.json.get("know_your_class_and_section", False)
    fields = request.json.get("fields")

    # Validate the input provided by the user
    try:
        validate_input(username, password, profile, know_your_class_and_section, fields)
    except Exception as e:
        stacktrace = traceback.format_exc()
        logging.error(f"Could not validate request data: {e}: {stacktrace}")
        return (
            json.dumps(
                {
                    "status": False,
                    "message": f"Could not validate request data: {e}",
                    "timestamp": str(current_time),
                }
            ),
            400,
        )

    # Authenticate the user
    try:
        authentication_result = pesu_academy.authenticate(
            username, password, profile, know_your_class_and_section, fields
        )
        authentication_result["timestamp"] = str(current_time)
        return json.dumps(authentication_result), 200
    except Exception as e:
        stacktrace = traceback.format_exc()
        logging.error(f"Error authenticating user: {e}: {stacktrace}")
        return (
            json.dumps({"status": False, "message": f"Error authenticating user: {e}"}),
            500,
        )


if __name__ == "__main__":
    pesu_academy = PESUAcademy()
    app.run(host="0.0.0.0", port=5000)
