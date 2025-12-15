import os
from playwright.async_api import async_playwright

<<<<<<< HEAD
=======
import base64
import requests
import uuid

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

def upload_to_github(local_path: str) -> str:
    filename = f"{uuid.uuid4()}.png"
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/screenshots/{filename}"

    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }

    data = {
        "message": f"Add screenshot {filename}",
        "content": content,
        "branch": GITHUB_BRANCH,
    }

    response = requests.put(api_url, headers=headers, json=data)
    response.raise_for_status()

    # Raw public URL
    return f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/screenshots/{filename}"
>>>>>>> a01e820 (change)

class HRMAutomation:
    def __init__(self, username, password, headless=True):
        self.username = username
        self.password = password
        self.headless = headless

        # XPaths
        self.username_xpath = "/html/body/div[1]/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/form/div[1]/input"
        self.password_xpath = "/html/body/div[1]/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/form/div[2]/input"
        self.submit_button_xpath = "/html/body/div[1]/div/div/div/div[2]/div/div[2]/div/div/div[2]/div/form/div[4]/button"
        self.clock_xpath = "/html/body/div[2]/section/div[1]/div/div[2]/form/button"

    async def run_async(self):
        screenshots_dir = "/tmp/screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--single-process',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                    ],
                )

                page = await browser.new_page()
                await page.goto("http://hrm.codebraininfotech.com/login")

                # Screenshot before login
                await page.screenshot(path=f"{screenshots_dir}/login_page.png")

                await page.fill(f'xpath={self.username_xpath}', self.username)
                await page.fill(f'xpath={self.password_xpath}', self.password)
                await page.click(f'xpath={self.submit_button_xpath}')

                await page.wait_for_selector(
                    f'xpath={self.clock_xpath}', timeout=15000
                )

                # Screenshot after login
                await page.screenshot(path=f"{screenshots_dir}/after_login.png")

                await browser.close()
                return {
                    "status": "success",
                    "message": "Automation completed successfully. Screenshots saved."
                }

        except Exception as e:
            try:
                await page.screenshot(path=f"{screenshots_dir}/error.png")

            except:
                pass

            return {
                "status": "error",
                "message": f"Automation failed: {str(e)}"
            }
