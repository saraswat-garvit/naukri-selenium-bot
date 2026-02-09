from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import os
import requests

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
NAUKRI_COOKIES = os.getenv("NAUKRI_COOKIES")
RESUME_URL = "https://drive.google.com/uc?export=download&id=1WC1fGkOEkGcLdzRrJhhU1C6HAUw7MpG-"
RESUME_PATH = "resume.pdf"

def download_resume():
    """Download resume from Google Drive"""
    print("📥 Downloading resume...")
    try:
        r = requests.get(RESUME_URL, timeout=30)
        r.raise_for_status()
        with open(RESUME_PATH, "wb") as f:
            f.write(r.content)
        file_size = os.path.getsize(RESUME_PATH)
        print(f"✅ Resume downloaded ({file_size} bytes)")
        return True
    except Exception as e:
        print(f"❌ Resume download failed: {e}")
        return False

def automate_with_cookies():
    """Main automation using saved cookies"""
    
    if not NAUKRI_COOKIES:
        print("❌ NAUKRI_COOKIES secret not found!")
        print("Please add cookies to GitHub Secrets")
        return False
    
    if not download_resume():
        return False
    
    # Setup Chrome
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )
    
    print("🚀 Starting Chrome...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    wait = WebDriverWait(driver, 40)
    
    try:
        # Step 1: Load Naukri homepage
        print("🌐 Opening Naukri.com...")
        driver.get("https://www.naukri.com")
        time.sleep(3)
        
        # Step 2: Load cookies
        print("🍪 Loading authentication cookies...")
        try:
            cookies = json.loads(NAUKRI_COOKIES)
            for cookie in cookies:
                try:
                    # Some cookies might be invalid for current domain
                    if 'sameSite' in cookie:
                        del cookie['sameSite']
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"⚠️ Skipping cookie: {e}")
            print(f"✅ Loaded {len(cookies)} cookies")
        except Exception as e:
            print(f"❌ Failed to load cookies: {e}")
            return False
        
        # Step 3: Refresh to apply cookies
        print("🔄 Refreshing page with cookies...")
        driver.refresh()
        time.sleep(5)
        driver.save_screenshot("step1_after_cookies.png")
        
        # Step 4: Navigate to profile
        print("🔍 Navigating to profile page...")
        driver.get("https://www.naukri.com/mnjuser/profile")
        time.sleep(8)
        driver.save_screenshot("step2_profile_page.png")
        
        current_url = driver.current_url
        print(f"📍 Current URL: {current_url}")
        
        # Step 5: Check if logged in
        if "nlogin" in current_url or "login" in current_url.lower():
            print("❌ COOKIES EXPIRED OR INVALID!")
            print("Please update NAUKRI_COOKIES secret")
            driver.save_screenshot("cookies_expired.png")
            return False
        
        print("✅ Successfully logged in with cookies!")
        
        # Step 6: Find file upload input
        print("🔍 Looking for resume upload input...")
        
        # Try multiple selectors
        file_input = None
        selectors = [
            (By.XPATH, "//input[@type='file']"),
            (By.CSS_SELECTOR, "input[type='file']"),
            (By.XPATH, "//input[@name='file']"),
            (By.CSS_SELECTOR, "input[name='file']"),
        ]
        
        for by, selector in selectors:
            try:
                file_input = wait.until(EC.presence_of_element_located((by, selector)))
                print(f"✅ Found upload input using: {selector}")
                break
            except:
                continue
        
        if not file_input:
            print("❌ Could not find file upload input!")
            print("Trying to find all file inputs...")
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            file_inputs = [inp for inp in all_inputs if inp.get_attribute("type") == "file"]
            print(f"Found {len(file_inputs)} file inputs")
            
            if file_inputs:
                file_input = file_inputs[0]
                print("✅ Using first file input found")
            else:
                driver.save_screenshot("no_upload_input.png")
                with open("profile_source.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                return False
        
        # Step 7: Upload resume
        resume_path = os.path.abspath(RESUME_PATH)
        print(f"📤 Uploading resume: {resume_path}")
        
        if not os.path.exists(resume_path):
            print(f"❌ Resume file not found!")
            return False
        
        file_input.send_keys(resume_path)
        print("✅ Resume file sent to input")
        
        # Step 8: Wait for upload
        print("⏳ Waiting for upload to complete...")
        time.sleep(12)
        driver.save_screenshot("step3_after_upload.png")
        
        # Additional wait
        time.sleep(5)
        driver.save_screenshot("step4_final.png")
        
        print("\n" + "="*60)
        print("✅ ✅ ✅ RESUME UPDATED SUCCESSFULLY! ✅ ✅ ✅")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        print(traceback.format_exc())
        
        try:
            driver.save_screenshot("error.png")
            with open("error_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("📸 Error screenshot saved")
        except:
            pass
        
        return False
        
    finally:
        print("🔚 Closing browser...")
        driver.quit()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 NAUKRI AUTOMATED RESUME UPDATER")
    print("="*60 + "\n")
    
    success = automate_with_cookies()
    
    if success:
        print("\n✅ DONE! Resume updated successfully!")
        exit(0)
    else:
        print("\n❌ FAILED! Check logs above")
        exit(1)
