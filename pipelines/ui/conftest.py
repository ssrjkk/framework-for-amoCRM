import pytest
from playwright.sync_api import sync_playwright, Page
from config.settings import BASE_URL, BROWSERS
import allure
import os


def pytest_configure(config):
    config.addinivalue_line("markers", "ui: UI tests (Playwright)")
    config.addinivalue_line("markers", "critical: Critical UI scenarios")


@pytest.fixture(scope="session")
def browser_type(browser_name):
    return browser_name


@pytest.fixture(scope="session")
def browser(browser_name):
    with sync_playwright() as p:
        browser = getattr(p, browser_name).launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture(scope="session")
def ui_base_url():
    return BASE_URL


@pytest.fixture(scope="session", params=BROWSERS)
def ui_browser(request):
    return request.param


def pytest_generate_tests(metafunc):
    if "ui_browser" in metafunc.fixturenames:
        metafunc.parametrize("ui_browser", BROWSERS)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = None
        if hasattr(item, "funcargs") and "page" in item.funcargs:
            page = item.funcargs["page"]
        elif hasattr(item, "funcargs") and "context" in item.funcargs:
            ctx = item.funcargs["context"]
            page = ctx.pages[0] if ctx.pages else None

        if page:
            screenshot = page.screenshot()
            allure.attach(
                screenshot,
                name=f"{item.name}_failed",
                attachment_type=allure.AttachmentType.PNG
            )


@pytest.fixture(scope="session")
def test_credentials():
    return {
        "valid_user": {"email": "test@example.com", "password": "TestPass123!"},
        "invalid_user": {"email": "invalid@example.com", "password": "wrong"},
    }