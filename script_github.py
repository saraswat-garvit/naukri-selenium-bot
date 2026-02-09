import requests
import os
import json
import re

NAUKRI_COOKIES = os.getenv("NAUKRI_COOKIES")
RESUME_URL = "https://drive.google.com/uc?export=download&id=1WC1fGkOEkGcLdzRrJhhU1C6HAUw7MpG-"
RESUME_FILE = "resume.pdf"

PROFILE_URL = "https://www.naukri.com/mnjuser/profile"
UPLOAD_URL = "https://www.naukri.com/mnjuser/profile"   # upload endpoint discovered dynamically


def download_resume():
    r = requests.get(RESUME_URL)
    with open(RESUME_FILE, "wb") as f:
        f.write(r.content)


def cookies_to_dict(cookie_json):
    cookies = json.loads(cookie_json)
    return {c['name']: c['value'] for c in cookies}


def upload_resume():

    download_resume()

    session = requests.Session()

    cookie_dict = cookies_to_dict(NAUKRI_COOKIES)
    session.cookies.update(cookie_dict)

    # Step 1 — open profile page
    resp = session.get(PROFILE_URL)
    html = resp.text

    if "Access Denied" in html:
        print("❌ Access blocked")
        return

    # Step 2 — extract csrf token (dynamic)
    token_match = re.search(r'csrfToken["\']?\s*:\s*["\'](.*?)["\']', html)

    if not token_match:
        print("❌ CSRF token not found")
        return

    csrf_token = token_match.group(1)
    print("✅ CSRF token:", csrf_token)

    # Step 3 — upload resume
    files = {
        "resume": open(RESUME_FILE, "rb")
    }

    headers = {
        "x-csrf-token": csrf_token,
        "referer": PROFILE_URL,
        "user-agent": "Mozilla/5.0"
    }

    upload = session.post(UPLOAD_URL, files=files, headers=headers)

    print("Upload response:", upload.status_code)


if __name__ == "__main__":
    upload_resume()
