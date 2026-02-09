
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
    print("📥 Downloading resume...")
    r = requests.get(RESUME_URL)
    with open(RESUME_PATH, "wb") as f:
        f.write(r.content)
    print(f"✅ Resume downloaded: {os.path.abspath(RESUME_PATH)}")

def automate():
    download_resume()
    
    options = Options()
    # Essential headless arguments
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
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Additional anti-detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    wait = WebDriverWait(driver, 60)
    
    try:
        print("🌐 Opening Naukri login page...")
        driver.get("https://www.naukri.com/nlogin/login")
        
        # Save screenshot for debugging
        driver.save_screenshot("step1_login_page.png")
        print(f"📸 Screenshot saved. Page title: {driver.title}")
        
        time.sleep(5)
        
        print("🔍 Looking for username field...")
        username_field = wait.until(EC.presence_of_element_located((By.ID, "usernameField")))
        username_field.send_keys(EMAIL)
        print(f"✅ Email entered: {EMAIL}")
        
        print("🔍 Looking for password field...")
        password_field = driver.find_element(By.ID, "passwordField")
        password_field.send_keys(PASSWORD)
        print("✅ Password entered")
        
        driver.save_screenshot("step2_credentials_filled.png")
        
        print("🔍 Looking for login button...")
        login_button = driver.find_element(By.XPATH, "//button[contains(@class,'blue-btn')]")
        login_button.click()
        print("✅ Login button clicked")
        
        time.sleep(10)
        driver.save_screenshot("step3_after_login.png")
        print(f"📸 After login. Current URL: {driver.current_url}")
        
        print("🔍 Looking for profile link...")
        profile_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'profile')]"))
        )
        profile_link.click()
        print("✅ Profile link clicked")
        
        time.sleep(5)
        driver.save_screenshot("step4_profile_page.png")
        
        print("🔍 Looking for file upload input...")
        resume_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
        )
        resume_path = os.path.abspath(RESUME_PATH)
        resume_input.send_keys(resume_path)
        print(f"✅ Resume uploaded: {resume_path}")
        
        time.sleep(5)
        driver.save_screenshot("step5_resume_uploaded.png")
        
        print("✅ Resume updated successfully!")
        
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Save page source for debugging
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("📄 Page source saved to page_source.html")
        
        driver.save_screenshot("error.png")
        print("📸 Error screenshot saved")
        raise
    finally:
        driver.quit()
        print("🔚 Browser closed")

if __name__ == "__main__":
    automate()
