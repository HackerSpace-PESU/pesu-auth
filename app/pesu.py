import logging
import os
import re
import time
import traceback
from datetime import datetime
from typing import Any, Optional

import requests_html
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


class PESUAcademy:
    def __init__(self):
        self.chrome: Optional[webdriver.Chrome] = None
        self.chrome_options: Optional[webdriver.ChromeOptions] = None

        self.branch_short_code_map: dict[str, str] = {
            "Computer Science and Engineering": "CSE",
            "Electronics and Communication Engineering": "ECE",
            "Mechanical Engineering": "ME",
            "Electrical and Electronics Engineering": "EEE",
            "Civil Engineering": "CE",
            "Biotechnology": "BT",
        }

    def init_chrome(self, headless: bool = True):
        logging.info(f"Initializing Chrome with headless={headless}")
        self.chrome_options = webdriver.ChromeOptions()

        if headless:
            self.chrome_options.add_argument("--headless")

        self.chrome_options.add_argument("--window-size=1920x1080")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--ignore-ssl-errors=yes")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_options.add_argument("--allow-running-insecure-content")
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) "
                                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36")

        if os.path.expanduser("~").startswith("/bot"):
            self.chrome_options.binary_location = "/bot/.apt/usr/bin/google-chrome"
            self.chrome = webdriver.Chrome(
                executable_path="bot/.chromedriver/bin/chromedriver",
                options=self.chrome_options,
            )
        else:
            if "chromedriver" not in os.listdir():
                self.chrome = webdriver.Chrome(options=self.chrome_options)
            else:
                self.chrome = webdriver.Chrome(
                    executable_path="./chromedriver", options=self.chrome_options
                )
        self.chrome.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": "Asia/Kolkata"})

    def map_branch_to_short_code(self, branch: str) -> Optional[str]:
        return self.branch_short_code_map.get(branch)

    def get_profile_information_from_selenium(self, username: Optional[str] = None) -> dict[str, Any]:
        try:
            logging.info("Navigating to profile data")
            menu_options = self.chrome.find_elements(By.CLASS_NAME, "menu-name")
            for option in menu_options:
                if option.text == "My Profile":
                    option.click()
                    break
            time.sleep(3)
            self.chrome.implicitly_wait(3)
        except Exception as e:
            logging.error(f"Unable to find the profile button: {traceback.format_exc()}")
            self.chrome.quit()
            return {"status": False, "message": "Unable to find the profile button after login.", "error": str(e)}

        try:
            logging.info("Fetching profile data from page")
            profile = dict()
            for field in self.chrome.find_elements(By.CLASS_NAME, "form-group")[6:13]:
                if (text := field.text) and "\n" in text:
                    key, value = list(map(str.strip, text.split("\n")))
                    key = "_".join(key.split()).lower()
                    if key in ["name", "srn", "pesu_id", "program", "branch", "semester", "section"]:
                        if key == "branch" and (branch_short_code := self.map_branch_to_short_code(value)):
                            profile["branch_short_code"] = branch_short_code
                        key = "prn" if key == "pesu_id" else key
                        profile[key] = value

            # if username starts with PES1, then he is from RR campus, else if it is PES2, then EC campus
            key = username if username else profile["pesu_id"]
            if campus_code_match := re.match(r"PES(\d)", key):
                campus_code = campus_code_match.group(1)
                profile["campus_code"] = int(campus_code)
                profile["campus"] = "RR" if campus_code == "1" else "EC"

            logging.info("Profile data fetched successfully")
            self.chrome.quit()
            return {"status": True, "profile": profile, "message": "Login successful."}
        except Exception as e:
            logging.error(f"Unable to fetch profile data: {traceback.format_exc()}")
            self.chrome.quit()
            return {"status": False, "message": "Unable to fetch profile data.", "error": str(e)}

    def get_profile_information_from_requests(
            self,
            session: requests_html.HTMLSession,
            username: Optional[str] = None
    ) -> dict[str, Any]:
        try:
            profile_url = "https://www.pesuacademy.com/Academy/s/studentProfilePESUAdmin"
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
            return {"status": False, "message": "Unable to fetch profile data.", "error": str(e)}

        profile = dict()
        for element in soup.find_all("div", attrs={"class": "form-group"})[:7]:
            if element.text.strip().startswith("PESU Id"):
                key = "pesu_id"
                value = element.text.strip().split()[-1]
            else:
                key, value = element.text.strip().split(" ", 1)
                key = "_".join(key.split()).lower()
            value = value.strip()
            if key in ["name", "srn", "pesu_id", "program", "branch", "semester", "section"]:
                if key == "branch" and (branch_short_code := self.map_branch_to_short_code(value)):
                    profile["branch_short_code"] = branch_short_code
                key = "prn" if key == "pesu_id" else key
                profile[key] = value

        # if username starts with PES1, then he is from RR campus, else if it is PES2, then EC campus
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
                    "x-requested-with": "XMLHttpRequest"
                },
                data={
                    "loginId": username
                }
            )
        except Exception:
            logging.error(f"Unable to get profile from Know Your Class and Section: {traceback.format_exc()}")
            return {}

        soup = BeautifulSoup(response.text, "html.parser")
        profile = dict()
        for th, td in zip(soup.find_all("th"), soup.find_all("td")):
            key = th.text.strip()
            key = key.replace(" ", "_").lower()
            value = td.text.strip()
            profile[key] = value

        return profile

    def authenticate_selenium_non_interactive(
            self,
            username: str,
            password: str,
            profile: bool = False
    ) -> dict[str, Any]:
        logging.warning("This method is deprecated and will be removed in future versions.")

        self.init_chrome()
        try:
            logging.info("Connecting to PESU Academy")
            self.chrome.get("https://pesuacademy.com/Academy")
            self.chrome.implicitly_wait(3)
        except Exception as e:
            logging.error(f"Unable to connect to PESU Academy: {traceback.format_exc()}")
            self.chrome.quit()
            return {"status": False, "message": "Unable to connect to PESU Academy.", "error": str(e)}

        try:
            logging.info("Logging in to PESU Academy")
            self.chrome.find_element(By.ID, "j_scriptusername").send_keys(username)
            self.chrome.find_element(By.NAME, "j_password").send_keys(password)
            self.chrome.find_element(By.ID, "postloginform#/Academy/j_spring_security_check").click()
            self.chrome.implicitly_wait(3)
        except Exception as e:
            logging.error(f"Unable to find the login form: {traceback.format_exc()}")
            self.chrome.quit()
            return {"status": False, "message": "Unable to find the login form.", "error": str(e)}

        status = False
        try:
            logging.info(f"Checking if the login was successful")
            if (element := self.chrome.find_element(By.CLASS_NAME, "login-msg")) \
                    and element.text in ("Your Username and Password do not match", "User doesn't exist"):
                # this element is shown only when the login is unsuccessful
                logging.error("Login unsuccessful")
                self.chrome.quit()
                status = False
                return {
                    "status": status,
                    "message": "Invalid username or password, or the user does not exist.",
                }
        except Exception:
            # this element is not shown when the login is successful
            status = True
            logging.info("Login successful")

        if profile:
            result = self.get_profile_information_from_selenium(username)
            know_your_class_and_section_data = self.get_know_your_class_and_section(username)
            result["know_your_class_and_section"] = know_your_class_and_section_data
            return result
        else:
            self.chrome.quit()
            return {"status": status, "message": "Login successful."}

    def authenticate_selenium_interactive(self, profile: bool = False) -> dict[str, Any]:
        self.init_chrome(headless=False)

        try:
            logging.info("Connecting to PESU Academy")
            self.chrome.get("https://pesuacademy.com/Academy")
            self.chrome.implicitly_wait(3)
            WebDriverWait(self.chrome, 10).until(
                ec.element_to_be_clickable((By.ID, "postloginform#/Academy/j_spring_security_check")))
        except Exception as e:
            logging.error(f"Unable to connect to PESU Academy: {traceback.format_exc()}")
            self.chrome.quit()
            return {"status": False, "message": "Unable to connect to PESU Academy.", "error": str(e)}

        # wait for user to login manually
        try:
            logging.info("Waiting for user to login manually")
            WebDriverWait(self.chrome, 90).until(
                ec.url_contains("https://www.pesuacademy.com/Academy/s/studentProfilePESU"))
            self.chrome.implicitly_wait(3)
            status = True
        except Exception as e:
            logging.error(f"Unable to find the login form: {traceback.format_exc()}")
            self.chrome.quit()
            return {"status": False, "message": "Unable to find the login form.", "error": str(e)}

        if profile:
            return self.get_profile_information_from_selenium()
        else:
            self.chrome.quit()
            return {"status": status, "message": "Login successful."}

    def authenticate(self, username: str, password: str, profile: bool = False) -> dict[str, Any]:
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
            return {"status": False, "message": "Unable to fetch csrf token.", "error": str(e)}

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
            return {"status": False, "message": "Unable to authenticate.", "error": str(e)}

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
            result = self.get_profile_information_from_requests(session, username)
            know_your_class_and_section_data = self.get_know_your_class_and_section(
                username,
                session,
                csrf_token
            )
            result["know_your_class_and_section"] = know_your_class_and_section_data
            return result
        else:
            session.close()
            return {"status": status, "message": "Login successful."}
