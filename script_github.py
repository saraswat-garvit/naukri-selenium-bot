from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os
import requests

NAUKRI_COOKIES = os.getenv("NAUKRI_COOKIES")

RESUME_URL = "https://drive.google.com/uc?export=download&id=1WC1fGkOEkGcLdzRrJhhU1C6HAUw7MpG-"
RESUME_PATH = "resume.pdf"


def download_resume():
    print("📥 Downloading resume...")
    try:
        r = requests.get(RESUME_URL, timeout=30)
        r.raise_for_status()
        with open(RESUME_PATH, "wb") as f:
            f.write(r.content)
        print("✅ Resume downloaded")
        return True
    except Exception as e:
        print("❌ Resume download failed:", e)
        return False


def automate_with_cookies():

    if not NAUKRI_COOKIES:
        print("❌ NAUKRI_COOKIES missing")
        return False

    if not download_resume():
        return False

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    print("🚀 Starting Chrome...")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 40)

    try:
        print("🌐 Opening Naukri...")
        driver.get("https://www.naukri.com")
        time.sleep(3)

        print("🍪 Loading cookies...")
        cookies = json.loads(NAUKRI_COOKIES)
        for cookie in cookies:
            try:
                if "sameSite" in cookie:
                    del cookie["sameSite"]
                driver.add_cookie(cookie)
            except:
                pass

        print("🔄 Refreshing session...")
        driver.refresh()
        time.sleep(5)

        print("🔍 Opening profile...")
        driver.get("https://www.naukri.com/mnjuser/profile")
        time.sleep(10)

        driver.save_screenshot("profile_page.png")

        if "nlogin" in driver.current_url:
            print("❌ Cookies expired")
            return False

        print("✅ Logged in")

        # WAIT SPA render
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5)

        # scroll to load lazy elements
        driver.execute_script("window.scrollTo(0, 800);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 1600);")
        time.sleep(3)

        print("🔍 Searching Update Resume button...")

        update_btn = None
        possible_xpaths = [
            "//span[contains(text(),'Update resume')]",
            "//span[contains(text(),'Update Resume')]",
            "//button[contains(text(),'Update')]",
            "//*[contains(text(),'Update resume')]"
        ]

        for xp in possible_xpaths:
            try:
                update_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
                if update_btn:
                    break
            except:
                continue

        if not update_btn:
            print("❌ Update button not found")
            driver.save_screenshot("update_not_found.png")
            return False

        driver.execute_script("arguments[0].click();", update_btn)
        print("✅ Update button clicked")

        time.sleep(5)

        print("🔍 Waiting for file input...")

        file_input = wait.until(EC.presence_of_element_located((
            By.XPATH, "//input[@type='file']"
        )))

        print("✅ File input found")

        resume_path = os.path.abspath(RESUME_PATH)
        file_input.send_keys(resume_path)

        print("📤 Uploading resume...")
        time.sleep(15)

        driver.save_screenshot("after_upload.png")

        print("✅ RESUME UPDATE COMPLETED")
        return True

    except Exception as e:
        print("❌ ERROR:", e)
        try:
            driver.save_screenshot("error.png")
        except:
            pass
        return False

    finally:
        driver.quit()


if __name__ == "__main__":
    print("🤖 NAUKRI BOT STARTED")
    success = automate_with_cookies()
    exit(0 if success else 1)
