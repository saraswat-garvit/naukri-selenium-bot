from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import requests

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

RESUME_URL = "https://drive.google.com/uc?export=download&id=1WC1fGkOEkGcLdzRrJhhU1C6HAUw7MpG-"
RESUME_PATH = "resume.pdf"


def download_resume():
    r = requests.get(RESUME_URL)
    with open(RESUME_PATH, "wb") as f:
        f.write(r.content)


def automate():
    download_resume()

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    wait = WebDriverWait(driver, 60)

    driver.get("https://www.naukri.com/nlogin/login")
    time.sleep(8)

    # wait until login form appears (more stable)
    email_box = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @type='email']"))
    )
    email_box.send_keys(EMAIL)

    password_box = driver.find_element(By.XPATH, "//input[@type='password']")
    password_box.send_keys(PASSWORD)

    login_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'blue-btn')]"))
    )
    login_btn.click()

    time.sleep(8)

    # open profile
    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'profile')]"))
    ).click()

    resume_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    resume_input.send_keys(os.path.abspath(RESUME_PATH))

    time.sleep(6)
    driver.quit()


if __name__ == "__main__":
    automate()
