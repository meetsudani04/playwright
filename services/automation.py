import os
from playwright.async_api import async_playwright


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
        screenshots_dir = "temp/screenshots"
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
