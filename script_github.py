from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
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
    options.add_argument("--start-maximized")
    
    # Anti-detection measures
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # More realistic user agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )
    
    # Additional options
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=en-US")
    
    print("🚀 Initializing Chrome WebDriver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Advanced anti-detection
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    })
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
    
    wait = WebDriverWait(driver, 40)
    
    try:
        # Step 1: Open login page
        print("🌐 Opening Naukri login page...")
        driver.get("https://www.naukri.com/nlogin/login")
        time.sleep(8)
        driver.save_screenshot("step1_login_page.png")
        print(f"📸 Login page loaded. Title: {driver.title}")
        
        # Step 2: Enter credentials with human-like typing
        print("🔍 Locating username field...")
        username_field = wait.until(EC.presence_of_element_located((By.ID, "usernameField")))
        username_field.click()
        time.sleep(1)
        
        # Type slowly like a human
        for char in EMAIL:
            username_field.send_keys(char)
            time.sleep(0.1)
        
        print(f"✅ Email entered: {EMAIL[:3]}***{EMAIL[-10:]}")
        time.sleep(1)
        
        print("🔍 Locating password field...")
        password_field = driver.find_element(By.ID, "passwordField")
        password_field.click()
        time.sleep(1)
        
        # Type password slowly
        for char in PASSWORD:
            password_field.send_keys(char)
            time.sleep(0.1)
        
        print("✅ Password entered")
        time.sleep(2)
        
        driver.save_screenshot("step2_credentials_entered.png")
        
        # Step 3: Submit login using ENTER key instead of clicking
        print("🔐 Submitting login form...")
        password_field.send_keys(Keys.RETURN)
        print("✅ Login form submitted")
        
        # Wait longer for redirect
        time.sleep(15)
        driver.save_screenshot("step3_after_login.png")
        
        # Step 4: Check multiple URLs for successful login
        current_url = driver.current_url
        print(f"📍 Current URL: {current_url}")
        
        # Check if we're still on login page
        if "nlogin/login" in current_url:
            print("❌ LOGIN FAILED - Still on login page!")
            
            # Check for specific error messages
            try:
                # Look for error messages
                error_selectors = [
                    ".error",
                    ".errorMsg", 
                    "[class*='error']",
                    "[class*='Error']",
                    ".alert",
                    "[role='alert']"
                ]
                
                for selector in error_selectors:
                    try:
                        error_elem = driver.find_element(By.CSS_SELECTOR, selector)
                        if error_elem.text.strip():
                            print(f"⚠️ Error on page: {error_elem.text}")
                    except:
                        continue
                        
            except Exception as e:
                print(f"Could not check for error messages: {e}")
            
            print("\n🔍 Troubleshooting steps:")
            print("  1. Verify EMAIL and PASSWORD in GitHub Secrets are 100% correct")
            print("  2. Try logging in manually to check if account needs verification")
            print("  3. Check if CAPTCHA is being shown (download screenshot)")
            print("  4. Ensure account is not locked")
            
            driver.save_screenshot("login_failed_detailed.png")
            with open("login_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            
            return False
        
        print("✅ Login successful! Redirected to:", current_url)
        
        # Step 5: Navigate directly to resume upload page
        print("🔍 Navigating to resume upload page...")
        driver.get("https://www.naukri.com/mnjuser/profile")
        time.sleep(8)
        driver.save_screenshot("step4_profile_page.png")
        print(f"📍 Profile page URL: {driver.current_url}")
        
        # Step 6: Look for file upload input
        print("🔍 Looking for resume upload input...")
        
        # Wait for page to fully load
        time.sleep(5)
        
        # Try multiple methods to find file input
        file_input = None
        
        # Method 1: Direct XPath
        try:
            file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
            print("✅ Found file input (Method 1: XPath)")
        except:
            print("⚠️ Method 1 failed, trying Method 2...")
        
        # Method 2: CSS Selector
        if not file_input:
            try:
                file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
                print("✅ Found file input (Method 2: CSS)")
            except:
                print("⚠️ Method 2 failed, trying Method 3...")
        
        # Method 3: Find all file inputs
        if not file_input:
            try:
                file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
                if file_inputs:
                    file_input = file_inputs[0]
                    print(f"✅ Found file input (Method 3: Found {len(file_inputs)} file inputs)")
            except:
                print("⚠️ Method 3 failed")
        
        if not file_input:
            print("❌ Could not find file upload input!")
            driver.save_screenshot("no_file_input_found.png")
            with open("profile_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            return False
        
        # Step 7: Upload resume
        resume_path = os.path.abspath(RESUME_PATH)
        print(f"📤 Uploading resume from: {resume_path}")
        
        # Make sure file exists
        if not os.path.exists(resume_path):
            print(f"❌ Resume file not found at: {resume_path}")
            return False
        
        file_input.send_keys(resume_path)
        print("✅ Resume file path sent to input")
        
        # Wait for upload to complete
        print("⏳ Waiting for upload to process...")
        time.sleep(10)
        driver.save_screenshot("step5_after_upload.png")
        
        # Additional wait
        time.sleep(5)
        driver.save_screenshot("step6_final.png")
        
        print("\n" + "="*50)
        print("✅ RESUME UPDATE COMPLETED!")
        print("="*50)
        return True
        
    except Exception as e:
        print(f"\n❌ EXCEPTION OCCURRED: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())
        
        try:
            print(f"\nCurrent URL: {driver.current_url}")
            print(f"Page title: {driver.title}")
            
            driver.save_screenshot("error.png")
            print("📸 Error screenshot saved")
            
            with open("error_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("📄 Page source saved")
            
        except Exception as debug_error:
            print(f"Could not save debug info: {debug_error}")
        
        return False
        
    finally:
        print("\n🔚 Closing browser...")
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
        print("\n❌ Script failed. Check logs and screenshots.")
        print("\n💡 NEXT STEPS:")
        print("   1. Download the debug artifacts from GitHub Actions")
        print("   2. Check step3_after_login.png screenshot")
        print("   3. Verify your EMAIL and PASSWORD are correct")
        print("   4. Try logging in manually on Naukri.com")
        exit(1)
