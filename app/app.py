import argparse
import datetime
import logging
import os
import re

import gh_md_to_html
from typing import Optional
import pytz
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import uvicorn

from app.constants import PESUAcademyConstants
from app.pesu import PESUAcademy

IST = pytz.timezone("Asia/Kolkata")
app = FastAPI()
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
    Validate the input provided by the user.
    :param username: str: The username of the user.
    :param password: str: The password of the user.
    :param profile: bool: Whether to fetch the profile details of the user.
    :param fields: dict: The fields to fetch from the user's profile.
    """
    logging.info(
        f"Validating input: user={username}, password={'*****' if password else None}, profile={profile}, fields={fields}"
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
                isinstance(
                    field, str) and field in PESUAcademyConstants.DEFAULT_FIELDS
            ), f"Invalid field: '{field}'. Valid fields are: {PESUAcademyConstants.DEFAULT_FIELDS}."
    logging.info("Input validation successful. All parameters are valid.")


@app.get(
    "/readme",
    response_class=HTMLResponse,
    tags=["Documentation"],
    summary="Serve the rendered README.md as HTML",
    responses={
        200: {
            "description": "Successfully rendered README.md content",
            "content": {
                "text/html": {
                    "example": "<h1>README</h1>\n<p>This is rendered HTML.</p>"
                }
            },
        },
        500: {"description": "Internal server error while retrieving README.md"},
    },
)
async def readme():
    try:
        if "README.html" not in os.listdir():
            logging.info("README.html does not exist. Beginning conversion...")
            convert_readme_to_html()
        logging.info("Rendering README.html...")
        with open("README.html") as f:
            output = f.read()
            return HTMLResponse(output)
    except Exception:
        logging.exception("Error rendering home page.")
        return "Error occurred while retrieving home page", 500


class Credentials(BaseModel):
    username: str = Field(
        ..., example="PES1UG20CS123", description="The user's SRN or PRN"
    )
    password: str = Field(
        ..., example="yourpassword", description="The user's password"
    )
    profile: Optional[bool] = Field(
        False, description="Whether to fetch the user's profile"
    )
    fields: Optional[
        List[
            Literal[
                "name",
                "prn",
                "srn",
                "program",
                "branch_short_code",
                "branch",
                "semester",
                "section",
                "email",
                "phone",
                "campus_code",
                "campus",
            ]
        ]
    ] = Field(
        None,
        example=["name", "prn", "branch", "branch_short_code", "campus"],
        description="List of profile fields to return",
    )


@app.post(
    "/authenticate",
    tags=["Authentication"],
    summary="Authenticate a user with their PESU credentials using PESU Academy",
    responses={
        200: {
            "description": "Authentication successful",
            "content": {
                "application/json": {
                    "example": {
                        "status": True,
                        "message": "Login successful.",
                        "timestamp": "2024-07-28 22:30:10.103368+05:30",
                        "profile": {
                            "name": "Johnny Blaze",
                            "prn": "PES1201800001",
                            "srn": "PES1201800001",
                            "program": "Bachelor of Technology",
                            "branch_short_code": "CSE",
                            "branch": "Computer Science and Engineering",
                            "semester": "6",
                            "section": "A",
                            "email": "johnnyblaze@gmail.com",
                            "phone": "1234567890",
                            "campus_code": 1,
                            "campus": "RR",
                        },
                    }
                }
            },
        },
        400: {
            "description": "Bad request - Invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "status": False,
                        "message": "Could not validate request data",
                        "timestamp": "2024-07-28T22:30:10.103368+05:30",
                    }
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": False,
                        "message": "Error authenticating user",
                        "timestamp": "2024-07-28T22:30:10.103368+05:30",
                    }
                }
            },
        },
    },
)
async def authenticate(credentials: Credentials):
    # Extract the input provided by the user
    current_time = datetime.datetime.now(IST)
    username = credentials.username
    password = credentials.password
    profile = credentials.profile
    fields = credentials.fields

    # Validate the input provided by the user
    try:
        logging.info(
            "Received authentication request. Beginning input validation...")
        validate_input(username, password, profile, fields)
    except Exception as e:
        logging.exception("Could not validate request data.")
        return JSONResponse(
            {
                "status": False,
                "message": f"Could not validate request data: {e}",
                "timestamp": str(current_time),
            },
            400,
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
        return JSONResponse(authentication_result, 200)
    except Exception as e:
        logging.exception(f"Error authenticating user={username}.")
        return JSONResponse(
            {"status": False, "message": f"Error authenticating user: {e}"}, 500
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

    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s",
        filemode="w",
    )

    uvicorn.run('app.app:app', host=args.host,
                port=args.port, reload=args.debug)
