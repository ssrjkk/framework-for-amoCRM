from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from config.settings import SELENIUM_GRID, BROWSERS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


CAPABILITIES = {
    "chrome": {
        "browserName": "chrome",
        "browserVersion": "latest",
        "goog:chromeOptions": {
            "args": ["--no-sandbox", "--disable-dev-shm-usage"]
        }
    },
    "firefox": {
        "browserName": "firefox",
        "browserVersion": "latest",
        "moz:firefoxOptions": {
            "args": ["-headless"]
        }
    },
    "edge": {
        "browserName": "MicrosoftEdge",
        "browserVersion": "latest",
        "ms:edgeOptions": {
            "args": ["--no-sandbox", "--disable-dev-shm-usage"]
        }
    },
}


def get_options(browser: str):
    if browser == "chrome":
        options = ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
    elif browser == "firefox":
        options = FirefoxOptions()
        options.add_argument("--headless")
    elif browser == "edge":
        options = EdgeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    else:
        options = webdriver.ChromeOptions()
    return options


def get_driver(browser: str, use_grid: bool = True):
    caps = CAPABILITIES.get(browser)
    if not caps:
        raise ValueError(f"Unknown browser: {browser}")
    
    options = get_options(browser)
    
    if use_grid:
        logger.info(f"Connecting to Selenium Grid: {SELENIUM_GRID}")
        driver = webdriver.Remote(
            command_executor=SELENIUM_GRID,
            options=options
        )
    else:
        if browser == "chrome":
            driver = webdriver.Chrome(options=options)
        elif browser == "firefox":
            driver = webdriver.Firefox(options=options)
        elif browser == "edge":
            driver = webdriver.Edge(options=options)
        else:
            driver = webdriver.Chrome(options=options)
    
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(30)
    return driver


@pytest.fixture(scope="function")
def selenium_driver(selenium_browser):
    driver = get_driver(selenium_browser)
    yield driver
    driver.quit()
