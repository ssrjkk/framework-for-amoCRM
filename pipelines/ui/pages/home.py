from .base import BasePage, BaseElement
from config.settings import AMOCRM_SUBDOMAIN


class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.email_input = BaseElement(page, 'input[name="LOGIN"]')
        self.password_input = BaseElement(page, 'input[name="PASSWORD"]')
        self.submit_button = BaseElement(page, 'button[type="submit"]')
        self.error_message = BaseElement(page, '.error')
        self.login_link = BaseElement(page, 'a[href*="login"]')

    def open(self):
        self.goto(f"https://{AMOCRM_SUBDOMAIN}.amocrm.ru")
        return self

    def login(self, email: str, password: str):
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.submit_button.click()
        return self

    def get_error(self) -> str:
        return self.error_message.get_text() if self.error_message.is_visible() else ""


class MainPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.logo = BaseElement(page, '.logo')
        self.sidebar = BaseElement(page, '.sidebar')
        self.search_input = BaseElement(page, 'input[type="search"]')
        self.user_menu = BaseElement(page, '.user-menu')
        self.notifications = BaseElement(page, '.notifications')

    def open(self):
        self.goto(f"https://{AMOCRM_SUBDOMAIN}.amocrm.ru")
        return self

    def is_logged_in(self) -> bool:
        return self.sidebar.is_visible()

    def logout(self):
        if self.user_menu.is_visible():
            self.user_menu.click()
        return self


class ContactsListPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.add_btn = BaseElement(page, '[data-name="add_contact"]')
        self.search_input = BaseElement(page, 'input[placeholder*="поиск"]')
        self.contact_list = BaseElement(page, '.contacts-list')
        self.export_btn = BaseElement(page, '[data-name="export"]')

    def open(self):
        self.goto(f"https://{AMOCRM_SUBDOMAIN}.amocrm.ru/contacts/")
        return self

    def add_contact(self):
        self.add_btn.click()
        return self

    def search(self, query: str):
        self.search_input.fill(query)
        return self


class ContactCardPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.name_field = BaseElement(page, '[data-field="NAME"]')
        self.email_field = BaseElement(page, '[data-field="EMAIL"]')
        self.phone_field = BaseElement(page, '[data-field="PHONE"]')
        self.save_btn = BaseElement(page, '[data-name="save"]')
        self.cancel_btn = BaseElement(page, '[data-name="cancel"]')

    def open(self, contact_id: int = None):
        if contact_id:
            self.goto(f"https://{AMOCRM_SUBDOMAIN}.amocrm.ru/contacts/{contact_id}/")
        else:
            self.goto(f"https://{AMOCRM_SUBDOMAIN}.amocrm.ru/contacts/")
        return self

    def set_name(self, name: str):
        self.name_field.fill(name)
        return self

    def save(self):
        self.save_btn.click()
        return self


class LeadsListPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.add_btn = BaseElement(page, '[data-name="add_lead"]')
        self.search_input = BaseElement(page, 'input[placeholder*="поиск"]')
        self.pipeline_view = BaseElement(page, '.pipeline-view')
        self.list_view = BaseElement(page, '.list-view')

    def open(self):
        self.goto(f"https://{AMOCRM_SUBDOMAIN}.amocrm.ru/leads/")
        return self


class CompaniesListPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.add_btn = BaseElement(page, '[data-name="add_company"]')
        self.search_input = BaseElement(page, 'input[placeholder*="поиск"]')

    def open(self):
        self.goto(f"https://{AMOCRM_SUBDOMAIN}.amocrm.ru/companies/")
        return self


class TasksPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.add_task_btn = BaseElement(page, '[data-name="add_task"]')
        self.task_list = BaseElement(page, '.tasks-list')

    def open(self):
        self.goto(f"https://{AMOCRM_SUBDOMAIN}.amocrm.ru/tasks/")
        return self


class SettingsPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.profile_link = BaseElement(page, 'a[href*="profile"]')
        self.users_link = BaseElement(page, 'a[href*="users"]')

    def open(self):
        self.goto(f"https://{AMOCRM_SUBDOMAIN}.amocrm.ru/settings/")
        return self