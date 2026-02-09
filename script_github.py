from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
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
    print("📥 Downloading resume...")
    try:
        r = requests.get(RESUME_URL, timeout=30)
        r.raise_for_status()
        with open(RESUME_PATH, "wb") as f:
            f.write(r.content)
        print(f"✅ Resume downloaded ({os.path.getsize(RESUME_PATH)} bytes)")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def automate_with_cookies():
    if not NAUKRI_COOKIES:
        print("❌ NAUKRI_COOKIES not found!")
        return False
    
    if not download_resume():
        return False
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36")
    
    print("🚀 Starting Chrome...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 40)
    
    try:
        print("🌐 Opening Naukri...")
        driver.get("https://www.naukri.com")
        time.sleep(3)
        
        print("🍪 Loading cookies...")
        try:
            cookies = json.loads(NAUKRI_COOKIES)
            for cookie in cookies:
                try:
                    if 'sameSite' in cookie:
                        del cookie['sameSite']
                    driver.add_cookie(cookie)
                except:
                    pass
            print(f"✅ Loaded {len(cookies)} cookies")
        except Exception as e:
            print(f"❌ Cookie load failed: {e}")
            return False
        
        print("🔄 Refreshing...")
        driver.refresh()
        time.sleep(5)
        
        print("🔍 Going to profile...")
        driver.get("https://www.naukri.com/mnjuser/profile")
        time.sleep(10)
        driver.save_screenshot("profile_page.png")
        
        if "nlogin" in driver.current_url:
            print("❌ COOKIES EXPIRED!")
            return False
        
        print("✅ Logged in! Current URL:", driver.current_url)
        
        # Save page HTML for debugging
        with open("profile_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("📄 Page source saved")
        
        # Method 1: Look for "Update Resume" or "Upload Resume" button
        print("\n🔍 METHOD 1: Looking for Update/Upload Resume button...")
        update_buttons = [
            "//button[contains(text(), 'Update Resume')]",
            "//button[contains(text(), 'Upload Resume')]",
            "//a[contains(text(), 'Update Resume')]",
            "//a[contains(text(), 'Upload Resume')]",
            "//div[contains(text(), 'Update Resume')]",
            "//span[contains(text(), 'Update Resume')]",
            "//*[contains(@class, 'updateResume')]",
            "//*[contains(@class, 'uploadResume')]",
        ]
        
        for xpath in update_buttons:
            try:
                button = driver.find_element(By.XPATH, xpath)
                print(f"✅ Found button: {xpath}")
                button.click()
                print("✅ Clicked update button")
                time.sleep(5)
                driver.save_screenshot("after_button_click.png")
                break
            except:
                continue
        
        # Method 2: Look for file input (all methods)
        print("\n🔍 METHOD 2: Looking for file input...")
        file_input = None
        
        # Try with JavaScript to find hidden inputs
        try:
            all_file_inputs = driver.execute_script("""
                return Array.from(document.querySelectorAll('input[type="file"]'));
            """)
            print(f"Found {len(all_file_inputs)} file inputs via JavaScript")
            if all_file_inputs:
                file_input = all_file_inputs[0]
                print("✅ Using first file input")
        except Exception as e:
            print(f"JavaScript method failed: {e}")
        
        # Try standard Selenium methods
        if not file_input:
            selectors = [
                (By.CSS_SELECTOR, "input[type='file']"),
                (By.XPATH, "//input[@type='file']"),
                (By.CSS_SELECTOR, "input[name='file']"),
                (By.CSS_SELECTOR, "input[accept*='pdf']"),
                (By.XPATH, "//input[contains(@accept, 'pdf')]"),
            ]
            
            for by, selector in selectors:
                try:
                    inputs = driver.find_elements(by, selector)
                    if inputs:
                        file_input = inputs[0]
                        print(f"✅ Found using: {selector}")
                        break
                except:
                    continue
        
        # Method 3: Try to make hidden input visible
        if file_input:
            try:
                # Make it visible if hidden
                driver.execute_script("""
                    arguments[0].style.display = 'block';
                    arguments[0].style.visibility = 'visible';
                    arguments[0].style.opacity = '1';
                    arguments[0].style.height = 'auto';
                    arguments[0].style.width = 'auto';
                """, file_input)
                print("✅ Made input visible")
            except:
                pass
        
        if not file_input:
            print("\n❌ Could not find file input with any method!")
            
            # Try going to direct upload URL
            print("\n🔍 METHOD 3: Trying direct upload URL...")
            try:
                driver.get("https://www.naukri.com/mnjuser/profile?id=&altresid=")
                time.sleep(5)
                driver.save_screenshot("direct_upload_page.png")
                
                file_input = driver.find_element(By.XPATH, "//input[@type='file']")
                print("✅ Found input on direct URL")
            except:
                print("❌ Direct URL method also failed")
                return False
        
        # Upload resume
        resume_path = os.path.abspath(RESUME_PATH)
        print(f"\n📤 Uploading resume: {resume_path}")
        
        if not os.path.exists(resume_path):
            print("❌ Resume file not found!")
            return False
        
        try:
            file_input.send_keys(resume_path)
            print("✅ Resume file sent to input!")
        except Exception as e:
            print(f"❌ Failed to send file: {e}")
            return False
        
        print("⏳ Waiting for upload to process...")
        time.sleep(15)
        driver.save_screenshot("after_upload.png")
        
        # Check for success message
        try:
            success_indicators = [
                "//div[contains(text(), 'successfully')]",
                "//span[contains(text(), 'successfully')]",
                "//*[contains(text(), 'uploaded')]",
                "//*[contains(@class, 'success')]",
            ]
            
            for xpath in success_indicators:
                try:
                    elem = driver.find_element(By.XPATH, xpath)
                    if elem.is_displayed():
                        print(f"✅ Success message found: {elem.text}")
                        break
                except:
                    continue
        except:
            pass
        
        time.sleep(5)
        driver.save_screenshot("final_state.png")
        
        print("\n" + "="*60)
        print("✅ RESUME UPDATE COMPLETED!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        print(traceback.format_exc())
        
        try:
            driver.save_screenshot("error.png")
            with open("error_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        except:
            pass
        
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 NAUKRI AUTOMATED RESUME UPDATER")
    print("="*60 + "\n")
    
    success = automate_with_cookies()
    exit(0 if success else 1)
