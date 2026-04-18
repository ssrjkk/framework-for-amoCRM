from playwright.sync_api import Page, Locator
from typing import Optional
import allure


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def goto(self, path: str = ""):
        from config.settings import BASE_URL
        self.page.goto(f"{BASE_URL}{path}")
        return self

    def click(self, selector: str, timeout: int = 30000):
        self.page.click(selector, timeout=timeout)

    def fill(self, selector: str, value: str):
        self.page.fill(selector, value)

    def is_visible(self, selector: str) -> bool:
        return self.page.is_visible(selector)

    def wait_for_selector(self, selector: str, timeout: int = 30000):
        self.page.wait_for_selector(selector, timeout=timeout)

    def wait_for_url(self, pattern: str, timeout: int = 30000):
        self.page.wait_for_url(pattern, timeout=timeout)

    def get_text(self, selector: str) -> str:
        return self.page.text_content(selector)

    def get_attribute(self, selector: str, attr: str) -> str:
        return self.page.get_attribute(selector, attr)

    def screenshot(self, name: str = "screenshot"):
        path = f"reports/{name}.png"
        self.page.screenshot(path=path)
        allure.attach.file(path, name=name, attachment_type=allure.AttachmentType.PNG)


class BaseElement:
    def __init__(self, page: Page, selector: str):
        self.page = page
        self.selector = selector
        self.locator: Locator = page.locator(selector)

    def click(self):
        self.locator.click()

    def fill(self, value: str):
        self.locator.fill(value)

    def is_visible(self) -> bool:
        return self.locator.is_visible()

    def get_text(self) -> str:
        return self.locator.text_content()

    def wait_for(self, state: str = "visible", timeout: int = 30000):
        self.locator.wait_for(state=state, timeout=timeout)