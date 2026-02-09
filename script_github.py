import requests
import os
import time

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

def update_resume_via_api():
    """Update resume using Naukri's API"""
    download_resume()
    
    session = requests.Session()
    
    # Step 1: Login to get session
    print("🔐 Logging in to Naukri...")
    login_url = "https://www.naukri.com/nlogin/login"
    login_data = {
        "username": EMAIL,
        "password": PASSWORD
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "appid": "109",
        "systemid": "Naukri"
    }
    
    login_response = session.post(login_url, data=login_data, headers=headers)
    
    if "mynaukri" in login_response.url or login_response.status_code == 200:
        print("✅ Login successful!")
    else:
        print(f"❌ Login failed. Status: {login_response.status_code}")
        print(f"Response URL: {login_response.url}")
        return False
    
    # Step 2: Upload resume
    print("📤 Uploading resume...")
    upload_url = "https://www.naukri.com/mnjuser/profile/upload/resume"
    
    with open(RESUME_PATH, "rb") as resume_file:
        files = {"file": (RESUME_PATH, resume_file, "application/pdf")}
        upload_response = session.post(upload_url, files=files, headers=headers)
    
    if upload_response.status_code == 200:
        print("✅ Resume uploaded successfully!")
        return True
    else:
        print(f"❌ Upload failed. Status: {upload_response.status_code}")
        print(f"Response: {upload_response.text[:500]}")
        return False

if __name__ == "__main__":
    success = update_resume_via_api()
    if not success:
        print("\n⚠️ API method failed. Check your credentials or try the alternative method.")
        exit(1)
