import datetime
import json
import logging
import os
import re
import traceback

import gh_md_to_html
import pytz
from flasgger import Swagger
from flask import Flask, request
import argparse

from app.constants import PESUAcademyConstants
from app.pesu import PESUAcademy

IST = pytz.timezone("Asia/Kolkata")
app = Flask(__name__)
pesu_academy = PESUAcademy()


def convert_readme_to_html():
    """
    Convert the README.md file to HTML and save it as README.html so that it can be rendered on the home page.
    """
    logging.info("Beginning conversion of README.md to HTML...")
    readme_content = open("README.md").read().strip()
    readme_content = re.sub(r":\w+: ", "", readme_content)
    with open("README_tmp.md", "w") as f:
        f.write(readme_content)
    html = gh_md_to_html.main("README_tmp.md").strip()
    with open("README.html", "w") as f:
        f.write(html)
    logging.info("README.md converted to HTML successfully.")

def validate_input(
    username: str,
    password: str,
    profile: bool,
    fields: list[str],
):
    """
    Validate the input provided by the user.
    :param username: str: The username of the user.
    :param password: str: The password of the user.
    :param profile: bool: Whether to fetch the profile details of the user.
    :param fields: dict: The fields to fetch from the user's profile.
    """
    logging.info(
        f"Validating input: username={username}, password={'*****' if password else None}, profile={profile}, fields={fields}"
    )
    assert username is not None, "Username not provided."
    assert isinstance(username, str), "Username should be a string."
    assert password is not None, "Password not provided."
    assert isinstance(password, str), "Password should be a string."
    assert isinstance(profile, bool), "Profile should be a boolean."
    assert fields is None or (
        isinstance(fields, list) and fields
    ), "Fields should be a non-empty list or None."
    if fields is not None:
        for field in fields:
            assert (
                isinstance(field, str) and field in PESUAcademyConstants.DEFAULT_FIELDS
            ), f"Invalid field: '{field}'. Valid fields are: {PESUAcademyConstants.DEFAULT_FIELDS}."
    logging.info("Input validation successful. All parameters are valid.")


@app.route("/readme")
def readme():
    """
    Serve the rendered README.md as HTML.
    ---
    tags:
      - Documentation
    produces:
      - text/html
    responses:
      200:
        description: Successfully rendered README.md content
      500:
        description: Internal server error while retrieving README.md
    """
    try:
        if "README.html" not in os.listdir():
            logging.info("README.html not found, converting README.md to HTML...")
            convert_readme_to_html()
        logging.info("Rendering README.html...")
        with open("README.html") as f:
            output = f.read()
            return output, 200, {"Content-Type": "text/html"}
    except Exception as e:
        stacktrace = traceback.format_exc()
        logging.exception(f"Error rendering home page.")
        return "Error occurred while retrieving home page", 500


@app.route("/authenticate", methods=["POST"])
def authenticate():
    """
    Authenticate a user with their PESU credentials using PESU Academy.
    ---
    tags:
      - Authentication
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: credentials
        required: true
        description: PESU login credentials and optional flags
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: The user's SRN or PRN
              example: PES1UG20CS123
            password:
              type: string
              description: The user's password
              example: yourpassword
            profile:
              type: boolean
              description: Whether to fetch the user's profile
              default: false
            fields:
              type: array
              description: List of profile fields to return. Must be from the predefined set of allowed fields.
              items:
                type: string
                enum:
                  - name
                  - prn
                  - srn
                  - program
                  - branch_short_code
                  - branch
                  - semester
                  - section
                  - email
                  - phone
                  - campus_code
                  - campus
              example: ["name", "prn", "branch", "branch_short_code", "campus"]
    responses:
      200:
        description: Authentication successful
        schema:
          type: object
          properties:
            status:
              type: boolean
              example: true
            message:
              type: string
              example: Login successful.
            timestamp:
              type: string
              format: date-time
              example: "2024-07-28 22:30:10.103368+05:30"
            profile:
              type: object
              description: User profile (if profile=true)
              properties:
                name:
                  type: string
                  example: Johnny Blaze
                prn:
                  type: string
                  example: PES1201800001
                srn:
                  type: string
                  example: PES1201800001
                program:
                  type: string
                  example: Bachelor of Technology
                branch_short_code:
                  type: string
                  example: CSE
                branch:
                  type: string
                  example: Computer Science and Engineering
                semester:
                  type: string
                  example: "6"
                section:
                  type: string
                  example: A
                email:
                  type: string
                  example: johnnyblaze@gmail.com
                phone:
                  type: string
                  example: "1234567890"
                campus_code:
                  type: integer
                  example: 1
                campus:
                  type: string
                  example: RR

      400:
        description: Bad request - Invalid input data
        schema:
          type: object
          properties:
            status:
              type: boolean
              example: false
            message:
              type: string
              example: Could not validate request data
            timestamp:
              type: string
              format: date-time
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            status:
              type: boolean
              example: false
            message:
              type: string
              example: Error authenticating user
    """
    # Extract the input provided by the user
    current_time = datetime.datetime.now(IST)
    username = request.json.get("username")
    password = request.json.get("password")
    profile = request.json.get("profile", False)
    fields = request.json.get("fields")

    # Validate the input provided by the user
    try:
        logging.info(f"Received authentication request. Validating input...")
        validate_input(username, password, profile, fields)
    except Exception as e:
        stacktrace = traceback.format_exc()
        logging.exception(f"Could not validate request data.")
        return (
            json.dumps(
                {
                    "status": False,
                    "message": f"Could not validate request data: {e}",
                    "timestamp": str(current_time),
                }
            ),
            400,
            {"Content-Type": "application/json"},
        )

    # Authenticate the user
    try:
        logging.info("Authenticating user with PESU Academy...")
        authentication_result = pesu_academy.authenticate(
            username, password, profile, fields
        )
        authentication_result["timestamp"] = str(current_time)
        return (
            json.dumps(authentication_result),
            200,
            {"Content-Type": "application/json"},
        )
    except Exception as e:
        stacktrace = traceback.format_exc()
        logging.exception(f"Error authenticating user.")
        return (
            json.dumps({"status": False, "message": f"Error authenticating user: {e}"}),
            500,
            {"Content-Type": "application/json"},
        )

if __name__ == "__main__":
    # Set up argument parser for command line arguments
    parser = argparse.ArgumentParser(
        description="PESUAuth API - A simple API to authenticate PESU credentials using PESU Academy."
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to run the Flask application on. Default is 0.0.0.0",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to run the Flask application on. Default is 5000",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run the application in debug mode with detailed logging.",
    )
    args = parser.parse_args()

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "v1",
                "route": "/v1.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/",
    }
    # TODO: Add version to the API
    # TODO: Set host dynamically based on the machine's IP address or domain name
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "PESU Auth API",
            "description": "A simple API to authenticate PESU credentials using PESU Academy",
            # "version": "1.0.0"
        },
        # "host": "localhost:5000",
        "basePath": "/",
        "schemes": ["https", "http"],
    }
    swagger = Swagger(app, config=swagger_config, template=swagger_template)

    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s",
        filemode="w",
    )

    app.run(host=args.host, port=args.port, debug=args.debug)
