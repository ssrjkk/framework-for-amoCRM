from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
from config.settings import BASE_URL, BROWSERS
import allure
import os


class PlaywrightClient:
    def __init__(self, browser_name: str = "chromium"):
        self.browser_name = browser_name
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None

    def start(self):
        self.playwright = sync_playwright().start()
        browser_type = getattr(self.playwright, self.browser_name)
        self.browser = browser_type.launch(headless=False)
        self.context = self.browser.new_context(viewport={"width": 1920, "height": 1080})
        self.page = self.context.new_page()
        self.page.goto(BASE_URL)

    def stop(self):
        if self.page:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def screenshot(self, name: str = "screenshot"):
        if self.page:
            self.page.screenshot(path=f"reports/{name}.png")
            allure.attach.file(f"reports/{name}.png", name=name, attachment_type=allure AttachmentType.PNG)


@pytest.fixture(scope="session")
def browser_config():
    return {"headless": False, "base_url": BASE_URL}


@pytest.fixture(scope="session")
def ui_browser():
    return BROWSERS[0]