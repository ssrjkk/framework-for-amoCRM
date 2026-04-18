import pytest
from playwright.sync_api import Page, expect
from pipelines.ui.pages.home import HomePage, LoginPage, DashboardPage, ContactListPage


pytestmark = [pytest.mark.ui, pytest.mark.critical]


class TestCriticalUI:
    @pytest.fixture(autouse=True)
    def setup(self, page: Page, ui_base_url: str):
        self.page = page
        self.base_url = ui_base_url

    def test_homepage_loads(self, page: Page):
        page.goto(self.base_url)
        expect(page).to_have_title(/.*amoCRM|AMO/)
        expect(page.locator('body')).to_be_visible()

    def test_login_form_visible(self, page: Page):
        page.goto(f"{self.base_url}/login")
        expect(page.locator('input[name="email"]')).to_be_visible()
        expect(page.locator('input[name="password"]')).to_be_visible()
        expect(page.locator('button[type="submit"]')).to_be_visible()

    def test_login_valid_user(self, page: Page, test_credentials):
        login_page = LoginPage(page)
        login_page.open()
        login_page.login(
            test_credentials["valid_user"]["email"],
            test_credentials["valid_user"]["password"]
        )
        page.wait_for_url("**/dashboard", timeout=10000)
        dashboard = DashboardPage(page)
        assert dashboard.sidebar.is_visible()

    def test_login_invalid_credentials(self, page: Page, test_credentials):
        login_page = LoginPage(page)
        login_page.open()
        login_page.login(
            test_credentials["invalid_user"]["email"],
            test_credentials["invalid_user"]["password"]
        )
        error_text = login_page.get_error()
        assert "error" in error_text.lower() or "invalid" in error_text.lower()

    def test_dashboard_navigation(self, page: Page, test_credentials):
        login_page = LoginPage(page)
        login_page.open()
        login_page.login(
            test_credentials["valid_user"]["email"],
            test_credentials["valid_user"]["password"]
        )
        page.wait_for_url("**/dashboard")
        page.goto(f"{self.base_url}/contacts")
        expect(page.locator('[data-testid="add-contact"]')).to_be_visible()

    def test_contact_list_loads(self, page: Page, test_credentials):
        login_page = LoginPage(page)
        login_page.open()
        login_page.login(
            test_credentials["valid_user"]["email"],
            test_credentials["valid_user"]["password"]
        )
        page.wait_for_url("**/dashboard")
        contacts = ContactListPage(page)
        contacts.open()
        expect(page.locator('input[placeholder*="search"]')).to_be_visible()

    def test_logout_flow(self, page: Page, test_credentials):
        login_page = LoginPage(page)
        login_page.open()
        login_page.login(
            test_credentials["valid_user"]["email"],
            test_credentials["valid_user"]["password"]
        )
        page.wait_for_url("**/dashboard")
        dashboard = DashboardPage(page)
        dashboard.logout()
        page.wait_for_url("**/login")
        expect(page.locator('input[name="email"]')).to_be_visible()

    def test_no_horizontal_scroll(self, page: Page):
        page.goto(self.base_url)
        scroll_width = page.evaluate("document.documentElement.scrollWidth")
        client_width = page.evaluate("document.documentElement.clientWidth")
        assert scroll_width <= client_width, "Horizontal scroll detected"

    def test_page_load_performance(self, page: Page):
        page.goto(self.base_url)
        navigation = page.evaluate("""() => {
            const perf = performance.getEntriesByType('navigation')[0];
            return { domContentLoaded: perf.domContentLoadedEventEnd - perf.fetchStart };
        }""")
        assert navigation["domContentLoaded"] < 3000, f"Page load too slow: {navigation}ms"