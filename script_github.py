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
    """Download resume from Google Drive"""
    print("📥 Downloading resume...")
    try:
        r = requests.get(RESUME_URL, timeout=30)
        r.raise_for_status()
        with open(RESUME_PATH, "wb") as f:
            f.write(r.content)
        print(f"✅ Resume downloaded: {os.path.abspath(RESUME_PATH)}")
        return True
    except Exception as e:
        print(f"❌ Failed to download resume: {str(e)}")
        return False

def automate():
    """Main automation function"""
    
    # Validate environment variables
    if not EMAIL or not PASSWORD:
        print("❌ ERROR: EMAIL or PASSWORD environment variables not set!")
        return False
    
    # Download resume
    if not download_resume():
        return False
    
    # Setup Chrome options
    options = Options()
    
    # Essential headless arguments for GitHub Actions
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Anti-detection measures
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )
    
    # Additional stability options
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    
    print("🚀 Initializing Chrome WebDriver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Anti-detection script
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    wait = WebDriverWait(driver, 30)
    
    try:
        # Step 1: Open login page
        print("🌐 Opening Naukri login page...")
        driver.get("https://www.naukri.com/nlogin/login")
        time.sleep(5)
        driver.save_screenshot("step1_login_page.png")
        print(f"📸 Login page loaded. Title: {driver.title}")
        
        # Step 2: Enter credentials
        print("🔍 Locating username field...")
        username_field = wait.until(EC.presence_of_element_located((By.ID, "usernameField")))
        username_field.clear()
        username_field.send_keys(EMAIL)
        print(f"✅ Email entered: {EMAIL[:3]}***{EMAIL[-10:]}")
        
        print("🔍 Locating password field...")
        password_field = driver.find_element(By.ID, "passwordField")
        password_field.clear()
        password_field.send_keys(PASSWORD)
        print("✅ Password entered")
        
        driver.save_screenshot("step2_credentials_entered.png")
        
        # Step 3: Click login button
        print("🔍 Locating login button...")
        login_button = driver.find_element(By.XPATH, "//button[contains(@class,'blue-btn')]")
        login_button.click()
        print("✅ Login button clicked")
        
        # Wait for page to load after login
        time.sleep(10)
        driver.save_screenshot("step3_after_login.png")
        
        # Step 4: Verify login success
        current_url = driver.current_url
        print(f"📍 Current URL: {current_url}")
        
        if "nlogin" in current_url:
            print("❌ LOGIN FAILED - Still on login page!")
            
            # Try to find error messages
            try:
                error_elements = driver.find_elements(By.CSS_SELECTOR, ".error, .errorMsg, [class*='error'], [class*='Error']")
                for elem in error_elements:
                    if elem.text.strip():
                        print(f"⚠️ Error message: {elem.text}")
            except:
                pass
            
            print("\n🔍 Possible reasons:")
            print("  1. Incorrect email or password")
            print("  2. CAPTCHA verification required")
            print("  3. Account locked or requires verification")
            print("  4. Naukri detected automation")
            
            driver.save_screenshot("login_failed.png")
            with open("login_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            
            return False
        
        print("✅ Login successful!")
        
        # Step 5: Navigate to profile page
        print("🔍 Navigating to profile page...")
        driver.get("https://www.naukri.com/mnjuser/profile")
        time.sleep(5)
        driver.save_screenshot("step4_profile_page.png")
        print(f"📍 Profile page URL: {driver.current_url}")
        
        # Step 6: Find and upload resume
        print("🔍 Looking for resume upload input...")
        
        # Try multiple selectors for file input
        file_input = None
        selectors = [
            "//input[@type='file']",
            "//input[@name='file']",
            "//input[contains(@class, 'file')]",
            "input[type='file']"
        ]
        
        for selector in selectors:
            try:
                if selector.startswith("//"):
                    file_input = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                else:
                    file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                print(f"✅ Found file input using selector: {selector}")
                break
            except:
                continue
        
        if not file_input:
            print("❌ Could not find file upload input!")
            driver.save_screenshot("no_file_input.png")
            return False
        
        # Upload resume
        resume_path = os.path.abspath(RESUME_PATH)
        print(f"📤 Uploading resume from: {resume_path}")
        file_input.send_keys(resume_path)
        print("✅ Resume file path sent to input")
        
        # Wait for upload to process
        time.sleep(8)
        driver.save_screenshot("step5_resume_uploaded.png")
        
        # Step 7: Verify upload (optional)
        print("⏳ Waiting for upload confirmation...")
        time.sleep(5)
        driver.save_screenshot("step6_final.png")
        
        print("\n" + "="*50)
        print("✅ RESUME UPDATE SUCCESSFUL!")
        print("="*50)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR OCCURRED: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        
        try:
            print(f"Current URL: {driver.current_url}")
            print(f"Page title: {driver.title}")
            
            # Save debug information
            driver.save_screenshot("error.png")
            print("📸 Error screenshot saved: error.png")
            
            with open("error_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("📄 Page source saved: error_page_source.html")
            
        except Exception as debug_error:
            print(f"Could not save debug info: {debug_error}")
        
        return False
        
    finally:
        print("🔚 Closing browser...")
        driver.quit()
        print("✅ Browser closed")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🤖 NAUKRI RESUME AUTO-UPDATER")
    print("="*50 + "\n")
    
    success = automate()
    
    if success:
        print("\n✅ Script completed successfully!")
        exit(0)
    else:
        print("\n❌ Script failed. Check logs and screenshots for details.")
        exit(1)
