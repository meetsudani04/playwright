import os
import asyncio
from playwright.async_api import async_playwright
import boto3
from botocore.config import Config


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

        # S3 configuration
        self.s3 = boto3.client(
            "s3",
            region_name="us-east-1",
            endpoint_url="https://objstorage.leapcell.io",
            aws_access_key_id="9839b41c6e9549209320380da8a570b7",
            aws_secret_access_key="3876906b4b38c9b6042dd7e8bed93df9ea635682bc66d727d39022b3cac334ca"
        )
        self.s3_bucket = "os-wsp1999798490684116992-vssu-k47u-4kbzibr2"

    async def run_async(self):
        screenshots_dir = "/tmp/screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--single-process',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                    ],
                )

                page = await browser.new_page()
                await page.goto("http://hrm.codebraininfotech.com/login")

                # Screenshot before login
                login_path = os.path.join(screenshots_dir, "login_page.png")
                await page.screenshot(path=login_path)

                await page.fill(f'xpath={self.username_xpath}', self.username)
                await page.fill(f'xpath={self.password_xpath}', self.password)
                await page.click(f'xpath={self.submit_button_xpath}')

                await page.wait_for_selector(f'xpath={self.clock_xpath}', timeout=15000)

                # Screenshot after login
                after_login_path = os.path.join(screenshots_dir, "after_login.png")
                await page.screenshot(path=after_login_path)

                await browser.close()

                # Upload screenshots to S3
                for file in [login_path, after_login_path]:
                    self.upload_to_s3(file, os.path.basename(file))

                return {"status": "success", "message": "Automation completed and screenshots uploaded to S3."}

        except Exception as e:
            try:
                error_path = os.path.join(screenshots_dir, "error.png")
                await page.screenshot(path=error_path)
                self.upload_to_s3(error_path, "error.png")
            except:
                pass

            return {"status": "error", "message": f"Automation failed: {str(e)}"}

    def upload_to_s3(self, local_path, s3_key):
        with open(local_path, "rb") as f:
            self.s3.put_object(Bucket=self.s3_bucket, Key=s3_key, Body=f)
        print(f"Uploaded {s3_key} to S3 bucket {self.s3_bucket}")


if __name__ == "__main__":
    username = "meet04"
    password = "Meet@0204004"
    automation = HRMAutomation(username, password)
    asyncio.run(automation.run_async())
