import logging
import os
import re
import time
import traceback
from typing import Any, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By


class PESUAcademy:
    def __init__(self):
        self.chrome: Optional[webdriver.Chrome] = None
        self.chrome_options: Optional[webdriver.ChromeOptions] = None

        self.branch_short_code_map = {
            "Computer Science and Engineering": "CSE",
            "Electronics and Communication Engineering": "ECE",
            "Mechanical Engineering": "ME",
            "Electrical and Electronics Engineering": "EEE",
            "Civil Engineering": "CE",
            "Biotechnology": "BT",
        }

    def init_chrome(self):
        logging.info("Initializing Chrome")
        self.chrome_options = webdriver.ChromeOptions()
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

    def authenticate(self, username: str, password: str, profile: bool = False) -> dict[str, Any]:
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
                        if key in ["name", "srn", "pesu_id", "srn", "program", "branch", "semester", "section"]:
                            if key == "branch" and (branch_short_code := self.map_branch_to_short_code(value)):
                                profile["branch_short_code"] = branch_short_code
                            profile[key] = value

                # if username starts with PES1, then he is from RR campus, else if it is PES2, then EC campus
                if campus_code_match := re.match(r"PES(\d)", username):
                    campus_code = campus_code_match.group(1)
                    profile["campus_code"] = campus_code
                    profile["campus"] = "RR" if campus_code == "1" else "EC"

                logging.info("Profile data fetched successfully")
                return {"status": status, "profile": profile, "message": "Login successful."}
            except Exception as e:
                logging.error(f"Unable to fetch profile data: {traceback.format_exc()}")
                self.chrome.quit()
                return {"status": False, "message": "Unable to fetch profile data.", "error": str(e)}
        else:
            self.chrome.quit()
            return {"status": status, "message": "Login successful."}
