import pytest
from playwright.sync_api import Page, expect
from pipelines.ui.pages.home import (
    LoginPage, MainPage, ContactsListPage, 
    ContactCardPage, LeadsListPage, CompaniesListPage, TasksPage
)


pytestmark = [pytest.mark.ui, pytest.mark.critical]


class TestCriticalUI:
    def test_login_page_loads(self, page: Page):
        login_page = LoginPage(page)
        login_page.open()
        expect(page).to_have_url(/.*amocrm.*/)

    def test_login_form_visible(self, page: Page):
        login_page = LoginPage(page)
        login_page.open()
        expect(page.locator('input[name="LOGIN"]')).to_be_visible()
        expect(page.locator('input[name="PASSWORD"]')).to_be_visible()

    def test_main_page_loads(self, page: Page):
        main_page = MainPage(page)
        main_page.open()
        expect(page).to_have_url(/.*amocrm.*/)

    def test_contacts_list_page(self, page: Page):
        contacts = ContactsListPage(page)
        contacts.open()
        expect(page).to_have_url(/.*contacts.*/)

    def test_leads_list_page(self, page: Page):
        leads = LeadsListPage(page)
        leads.open()
        expect(page).to_have_url(/.*leads.*/)

    def test_companies_list_page(self, page: Page):
        companies = CompaniesListPage(page)
        companies.open()
        expect(page).to_have_url(/.*companies.*/)

    def test_tasks_page(self, page: Page):
        tasks = TasksPage(page)
        tasks.open()
        expect(page).to_have_url(/.*tasks.*/)

    def test_no_horizontal_scroll(self, page: Page):
        main_page = MainPage(page)
        main_page.open()
        scroll_width = page.evaluate("document.documentElement.scrollWidth")
        client_width = page.evaluate("document.documentElement.clientWidth")
        assert scroll_width <= client_width

    def test_page_load_performance(self, page: Page):
        import time
        start = time.time()
        page.goto(f"https://test.amocrm.ru")
        load_time = (time.time() - start) * 1000
        assert load_time < 10000, f"Page too slow: {load_time}ms"


@pytest.mark.parametrize("browser", ["chromium", "firefox", "webkit"])
class TestCrossBrowserUI:
    def test_all_browsers_login_page(self, page: Page, browser):
        page.goto(f"https://test.amocrm.ru")
        expect(page.locator('input[name="LOGIN"]')).to_be_visible()