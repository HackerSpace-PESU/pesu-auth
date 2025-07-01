import argparse
import datetime
import json
import logging
import os
import re

import gh_md_to_html
from typing import Optional
import pytz
from flasgger import Swagger
from flask import Flask, request

from app.pesu import PESUAcademy
from models.validate_input_model import ValidateInputModel

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
    fields: Optional[list[str]],
):
    """
    Validate the input provided by the user using Pydantic model.
    :param username: str: The username of the user.
    :param password: str: The password of the user.
    :param profile: bool: Whether to fetch the profile details of the user.
    :param fields: list: The fields to fetch from the user's profile.
    :return: ValidateInputModel: The validated input model.
    """
    logging.info(
        f"Validating input: user={username}, password={'*****' if password else None}, profile={profile}, fields={fields}"
    )

    validated_data = ValidateInputModel(
        username=username, password=password, profile=profile, fields=fields
    )

    logging.info("Input validation successful. All parameters are valid.")
    return validated_data


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
            logging.info("README.html does not exist. Beginning conversion...")
            convert_readme_to_html()
        logging.info("Rendering README.html...")
        with open("README.html") as f:
            output = f.read()
            return output, 200, {"Content-Type": "text/html"}
    except Exception:
        logging.exception("Error rendering home page.")
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
        description: PESU login credentials and optional flags (validated using ValidateInputModel)
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: The user's SRN, PRN, email, or phone number (validated and trimmed)
              example: PES1UG20CS123
            password:
              type: string
              description: The user's password (must not be empty)
              example: yourpassword
            profile:
              type: boolean
              description: Whether to fetch the user's profile (strict boolean validation)
              default: false
            fields:
              type: array
              description: List of profile fields to return (validated against predefined allowed fields)
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
          additionalProperties: false
          x-pydantic-model: ValidateInputModel
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
        description: Bad request - Invalid input data (Pydantic validation errors)
        schema:
          type: object
          properties:
            status:
              type: boolean
              example: false
            message:
              type: string
              example: "Could not validate request data: 1 validation error for ValidateInputModel"
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
        logging.info("Received authentication request. Beginning input validation...")
        validated_data = validate_input(username, password, profile, fields)
        username = validated_data.username
        password = validated_data.password
        profile = validated_data.profile
        fields = validated_data.fields
    except Exception as e:
        logging.exception("Could not validate request data.")
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
        logging.info(f"Authenticating user={username} with PESU Academy...")
        authentication_result = pesu_academy.authenticate(
            username, password, profile, fields
        )
        authentication_result["timestamp"] = str(current_time)
        logging.info(
            f"Returning auth result for user={username}: {authentication_result}"
        )
        return (
            json.dumps(authentication_result),
            200,
            {"Content-Type": "application/json"},
        )
    except Exception as e:
        logging.exception(f"Error authenticating user={username}.")
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

    # Run the app
    app.run(host=args.host, port=args.port, debug=args.debug)
