import pytest
import allure
from config.settings import BROWSERS, BASE_URL, SELENIUM_GRID
from pipelines.crossbrowser.utils.grid_client import get_driver


def pytest_configure(config):
    config.addinivalue_line("markers", "crossbrowser: Cross-browser Selenium tests")
    config.addinivalue_line("markers", "selenium: Selenium Grid tests")


@pytest.fixture(scope="session")
def grid_url():
    return SELENIUM_GRID


@pytest.fixture(scope="session")
def test_base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def supported_browsers():
    return BROWSERS


def pytest_generate_tests(metafunc):
    if "selenium_browser" in metafunc.fixturenames:
        metafunc.parametrize("selenium_browser", BROWSERS)


@pytest.fixture(scope="function")
def driver(selenium_browser):
    d = get_driver(selenium_browser, use_grid=True)
    yield d
    try:
        d.quit()
    except Exception:
        pass


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        driver = None
        if hasattr(item, "funcargs") and "driver" in item.funcargs:
            driver = item.funcargs.get("driver")
        
        if driver:
            try:
                screenshot = driver.get_screenshot_as_base64()
                allure.attach(
                    screenshot,
                    name=f"{item.name}_failed",
                    attachment_type=allure.AttachmentType.PNG
                )
                
                logs = driver.get_log("browser")
                errors = [l for l in logs if l.get("level") == "SEVERE"]
                if errors:
                    allure.attach(
                        str(errors),
                        name="console_errors",
                        attachment_type=allure.AttachmentType.TEXT
                    )
            except Exception as e:
                logger.warning(f"Failed to capture screenshot: {e}")


@pytest.fixture(scope="session")
def test_credentials():
    return {
        "valid_user": {"email": "test@example.com", "password": "TestPass123!"},
    }


import logging
logger = logging.getLogger(__name__)