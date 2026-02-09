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

    # FIXED DRIVER INIT
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    wait = WebDriverWait(driver, 30)

    driver.get("https://www.naukri.com/nlogin/login")

    wait.until(EC.presence_of_element_located((By.ID, "usernameField"))).send_keys(EMAIL)
    driver.find_element(By.ID, "passwordField").send_keys(PASSWORD)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".blue-btn"))).click()

    time.sleep(5)

    wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'profile')]"))
    ).click()

    resume_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    resume_input.send_keys(os.path.abspath(RESUME_PATH))

    time.sleep(5)
    driver.quit()


if __name__ == "__main__":
    automate()
