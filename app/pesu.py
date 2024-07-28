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

    @staticmethod
    def map_branch_to_short_code(branch: str) -> Optional[str]:
        """
        Map the branch name to its short code.
        :param branch: Branch name
        :return: Short code of the branch
        """
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
            if response.status_code != 200:
                raise Exception("Unable to fetch profile data.")
            soup = BeautifulSoup(response.text, "lxml")

        except Exception as e:
            logging.error(f"Unable to fetch profile data: {traceback.format_exc()}")
            return {
                "status": False,
                "message": "Unable to fetch profile data.",
                "error": str(e),
            }

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

        return {"status": True, "profile": profile, "message": "Login successful."}

    @staticmethod
    def get_know_your_class_and_section(
            username: str,
            session: Optional[requests_html.HTMLSession] = None,
            csrf_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Get the class and section information from the public Know Your Class and Section page.
        :param username: Username of the user
        :param session: The session object
        :param csrf_token: The csrf token
        :return: The class and section information
        """

        if not session:
            session = requests_html.HTMLSession()

        if not csrf_token:
            home_url = "https://www.pesuacademy.com/Academy/"
            response = session.get(home_url)
            soup = BeautifulSoup(response.text, "lxml")
            csrf_token = soup.find("meta", attrs={"name": "csrf-token"})["content"]

        try:
            response = session.post(
                "https://www.pesuacademy.com/Academy/getStudentClassInfo",
                headers={
                    "authority": "www.pesuacademy.com",
                    "accept": "*/*",
                    "accept-language": "en-IN,en-US;q=0.9,en-GB;q=0.8,en;q=0.7",
                    "content-type": "application/x-www-form-urlencoded",
                    "origin": "https://www.pesuacademy.com",
                    "referer": "https://www.pesuacademy.com/Academy/",
                    "sec-ch-ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Linux"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "x-csrf-token": csrf_token,
                    "x-requested-with": "XMLHttpRequest",
                },
                data={"loginId": username},
            )
        except Exception:
            logging.error(
                f"Unable to get profile from Know Your Class and Section: {traceback.format_exc()}"
            )
            return {}

        soup = BeautifulSoup(response.text, "html.parser")
        profile = dict()
        for th, td in zip(soup.find_all("th"), soup.find_all("td")):
            key = th.text.strip()
            key = key.replace(" ", "_").lower()
            value = td.text.strip()
            profile[key] = value

        return profile

    def authenticate(
            self, username: str, password: str, profile: bool = False
    ) -> dict[str, Any]:
        """
        Authenticate the user with the provided username and password.
        :param username: Username of the user, usually their PRN/email/phone number
        :param password: Password of the user
        :param profile: Whether to fetch the profile information or not
        :return: The authentication result
        """
        session = requests_html.HTMLSession()

        try:
            # Get the initial csrf token
            home_url = "https://www.pesuacademy.com/Academy/"
            response = session.get(home_url)
            soup = BeautifulSoup(response.text, "lxml")
            csrf_token = soup.find("meta", attrs={"name": "csrf-token"})["content"]
        except Exception as e:
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
            auth_url = "https://www.pesuacademy.com/Academy/j_spring_security_check"
            response = session.post(auth_url, data=data)
            soup = BeautifulSoup(response.text, "lxml")
        except Exception as e:
            logging.error(f"Unable to authenticate: {traceback.format_exc()}")
            session.close()
            return {
                "status": False,
                "message": "Unable to authenticate.",
                "error": str(e),
            }

        # if class login-form is present, login failed
        if soup.find("div", attrs={"class": "login-form"}):
            logging.error("Login unsuccessful")
            session.close()
            return {
                "status": False,
                "message": "Invalid username or password, or the user does not exist.",
            }

        logging.info("Login successful")
        status = True
        csrf_token = soup.find("meta", attrs={"name": "csrf-token"})["content"]

        if profile:
            result = self.get_profile_information(session, username)
            know_your_class_and_section_data = self.get_know_your_class_and_section(
                username, session, csrf_token
            )
            result["know_your_class_and_section"] = know_your_class_and_section_data
            return result
        else:
            session.close()
            return {"status": status, "message": "Login successful."}
