import logging
import re
import traceback
from datetime import datetime
from typing import Any, Optional

import requests_html
from bs4 import BeautifulSoup


class PESUAcademy:
    """
    Class to interact with the PESU Academy website.
    """

    # Default fields to fetch from the profile and know your class and section data
    DEFAULT_FIELDS = [
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
        "class",
        "cycle",
        "department",
        "institute_name",
    ]

    @staticmethod
    def map_branch_to_short_code(branch: str) -> Optional[str]:
        """
        Map the branch name to its short code.
        :param branch: Branch name
        :return: Short code of the branch
        """
        logging.warning(
            "Branch short code mapping will be deprecated in future versions."
        )
        branch_short_code_map: dict[str, str] = {
            "Computer Science and Engineering": "CSE",
            "Electronics and Communication Engineering": "ECE",
            "Mechanical Engineering": "ME",
            "Electrical and Electronics Engineering": "EEE",
            "Civil Engineering": "CE",
            "Biotechnology": "BT",
        }
        return branch_short_code_map.get(branch)

    def get_profile_information(
        self, session: requests_html.HTMLSession, username: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get the profile information of the user.
        :param session: The session object
        :param username: The username of the user
        :return: The profile information
        """
        try:
            # Fetch the profile data from the student profile page
            profile_url = (
                "https://www.pesuacademy.com/Academy/s/studentProfilePESUAdmin"
            )
            query = {
                "menuId": "670",
                "url": "studentProfilePESUAdmin",
                "controllerMode": "6414",
                "actionType": "5",
                "id": "0",
                "selectedData": "0",
                "_": str(int(datetime.now().timestamp() * 1000)),
            }
            response = session.get(profile_url, allow_redirects=False, params=query)
            # If the status code is not 200, raise an exception because the profile page is not accessible
            if response.status_code != 200:
                raise Exception(
                    "Unable to fetch profile data. Profile page not accessible."
                )
            # Parse the response text
            soup = BeautifulSoup(response.text, "lxml")

        except Exception as e:
            logging.error(f"Unable to fetch profile data: {traceback.format_exc()}")
            return {"error": f"Unable to fetch profile data: {traceback.format_exc()}"}

        profile = dict()
        for element in soup.find_all("div", attrs={"class": "form-group"})[:7]:
            if element.text.strip().startswith("PESU Id"):
                key = "pesu_id"
                value = element.text.strip().split()[-1]
            else:
                key, value = element.text.strip().split(" ", 1)
                key = "_".join(key.split()).lower()
            value = value.strip()
            if key in [
                "name",
                "srn",
                "pesu_id",
                "program",
                "branch",
                "semester",
                "section",
            ]:
                if key == "branch" and (
                    branch_short_code := self.map_branch_to_short_code(value)
                ):
                    profile["branch_short_code"] = branch_short_code
                key = "prn" if key == "pesu_id" else key
                profile[key] = value

        profile["email"] = soup.find("input", attrs={"id": "updateMail"}).get("value")
        profile["phone"] = soup.find("input", attrs={"id": "updateContact"}).get(
            "value"
        )

        # if username starts with PES1, then they are from RR campus, else if it is PES2, then EC campus
        key = username if username else profile["pesu_id"]
        if campus_code_match := re.match(r"PES(\d)", key):
            campus_code = campus_code_match.group(1)
            profile["campus_code"] = int(campus_code)
            profile["campus"] = "RR" if campus_code == "1" else "EC"

        return profile

    def authenticate(
        self,
        username: str,
        password: str,
        profile: bool = False,
        fields: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Authenticate the user with the provided username and password.
        :param username: Username of the user, usually their PRN/email/phone number
        :param password: Password of the user
        :param profile: Whether to fetch the profile information or not
        :param fields: The fields to fetch from the profile and know your class and section data. Defaults to all fields if not provided.
        :return: The authentication result
        """
        # Create a new session
        session = requests_html.HTMLSession()
        # Default fields to fetch if fields is not provided
        fields = self.DEFAULT_FIELDS if fields is None else fields
        # check if fields is not the default fields and enable field filtering
        field_filtering = fields != self.DEFAULT_FIELDS

        try:
            # Get the initial csrf token assigned to the user session when the home page is loaded
            home_url = "https://www.pesuacademy.com/Academy/"
            response = session.get(home_url)
            soup = BeautifulSoup(response.text, "lxml")
            # extract the csrf token from the meta tag
            csrf_token = soup.find("meta", attrs={"name": "csrf-token"})["content"]
        except Exception as e:
            # Log the error and return the error message
            logging.error(f"Unable to fetch csrf token: {traceback.format_exc()}")
            session.close()
            return {
                "status": False,
                "message": "Unable to fetch csrf token.",
                "error": str(e),
            }

        # Prepare the login data for auth call
        data = {
            "_csrf": csrf_token,
            "j_username": username,
            "j_password": password,
        }

        try:
            # Make a post request to authenticate the user
            auth_url = "https://www.pesuacademy.com/Academy/j_spring_security_check"
            response = session.post(auth_url, data=data)
            soup = BeautifulSoup(response.text, "lxml")
        except Exception as e:
            # Log the error and return the error message
            logging.error(f"Unable to authenticate: {traceback.format_exc()}")
            session.close()
            return {
                "status": False,
                "message": "Unable to authenticate.",
                "error": str(e),
            }

        # If class login-form is present, login failed
        if soup.find("div", attrs={"class": "login-form"}):
            # Log the error and return the error message
            logging.error("Login unsuccessful")
            session.close()
            return {
                "status": False,
                "message": "Invalid username or password, or the user does not exist.",
            }

        # If the user is successfully authenticated
        logging.info("Login successful")
        status = True
        # Get the newly authenticated csrf token
        csrf_token = soup.find("meta", attrs={"name": "csrf-token"})["content"]
        result = {"status": status, "message": "Login successful."}

        if profile:
            # Fetch the profile information
            result["profile"] = self.get_profile_information(session, username)
            # Filter the fields if field filtering is enabled
            if field_filtering:
                result["profile"] = {
                    key: value
                    for key, value in result["profile"].items()
                    if key in fields
                }

        # Close the session and return the result
        session.close()
        return result
