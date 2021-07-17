import os
import time
from dotenv import load_dotenv
from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-running-insecure-content')

load_dotenv()
GOOGLE_CHROME_BIN = os.environ["GOOGLE_CHROME_BIN"]
CHROMEDRIVER_PATH = os.environ["CHROMEDRIVER_PATH"]


def authenticatePESU(username, password):
    chrome = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)
    chrome.get("https://pesuacademy.com/Academy")
    time.sleep(2)

    username_box = chrome.find_element_by_xpath(r'//*[@id="j_scriptusername"]')
    password_box = chrome.find_element_by_xpath(r'//*[@name="j_password"]')

    username_box.send_keys(username)
    time.sleep(0.3)
    password_box.send_keys(password)
    time.sleep(0.3)

    sign_in_button = chrome.find_element_by_xpath(
        r'//*[@id="postloginform#/Academy/j_spring_security_check"]')
    sign_in_button.click()
    time.sleep(1)

    login_status = None
    profile_data = dict()
    try:
        menu_options = chrome.find_elements_by_xpath(
            r'//*[@class="menu-name"]')
        menu_options[9].click()
        login_status = True
    except:
        login_status = False

    if login_status:
        time.sleep(1)
        text_boxes = chrome.find_elements_by_xpath(
            r'//*[@class="col-md-12 col-xs-12 control-label text-left"]')

        text_content = [text_box.text.strip() for text_box in text_boxes[:7]]
        name, prn, srn, degree, branch, semester, section = text_content
        profile_data["name"] = name
        profile_data["prn"] = prn
        profile_data["srn"] = srn
        profile_data["degree"] = degree
        profile_data["branch"] = branch
        profile_data["semester"] = semester
        profile_data["section"] = section.split()[1]

    chrome.quit()
    return login_status, profile_data
