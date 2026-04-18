from .base import BasePage, BaseElement


class HomePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.logo = BaseElement(page, '[class*="logo"]')
        self.menu = BaseElement(page, 'nav')
        self.search_input = BaseElement(page, 'input[type="search"]')
        self.login_button = BaseElement(page, '[data-testid="login-btn"]')

    def open(self):
        self.goto("/")
        return self

    def is_logged_in(self) -> bool:
        return self.login_button.is_visible() is False


class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.email_input = BaseElement(page, 'input[name="email"]')
        self.password_input = BaseElement(page, 'input[name="password"]')
        self.submit_button = BaseElement(page, 'button[type="submit"]')
        self.error_message = BaseElement(page, '[data-testid="error"]')

    def open(self):
        self.goto("/login")
        return self

    def login(self, email: str, password: str):
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_button.click()
        return self

    def get_error(self) -> str:
        return self.error_message.get_text()


class DashboardPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.sidebar = BaseElement(page, '[data-testid="sidebar"]')
        self.user_menu = BaseElement(page, '[data-testid="user-menu"]')
        self.notifications = BaseElement(page, '[data-testid="notifications"]')

    def open(self):
        self.goto("/dashboard")
        return self

    def logout(self):
        self.user_menu.click()
        self.click('[data-testid="logout"]')
        return self


class ContactListPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.add_contact_btn = BaseElement(page, '[data-testid="add-contact"]')
        self.search_input = BaseElement(page, 'input[placeholder*="search"]')
        self.contact_cards = BaseElement(page, '[data-testid="contact-card"]')

    def open(self):
        self.goto("/contacts")
        return self

    def add_contact(self):
        self.add_contact_btn.click()
        return self