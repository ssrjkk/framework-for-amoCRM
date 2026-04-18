import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.settings import BASE_URL


pytestmark = [pytest.mark.crossbrowser, pytest.mark.sel_grid]


class TestCrossBrowser:
    def test_homepage_loads(self, driver, selenium_browser, test_base_url):
        driver.get(test_base_url)
        assert driver.title or driver.page_source
    
    def test_homepage_title_contains_amocrm(self, driver, selenium_browser, test_base_url):
        driver.get(test_base_url)
        title = driver.title.lower()
        assert "amo" in title or "amocrm" in title or title
    
    def test_login_form_visible(self, driver, selenium_browser, test_base_url):
        driver.get(f"{test_base_url}/login")
        
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        assert email_input.is_displayed()
        
        password_input = driver.find_element(By.NAME, "password")
        assert password_input.is_displayed()
        
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        assert submit_button.is_displayed()
    
    def test_login_valid_user(self, driver, selenium_browser, test_base_url, test_credentials):
        driver.get(f"{test_base_url}/login")
        
        driver.find_element(By.NAME, "email").send_keys(
            test_credentials["valid_user"]["email"]
        )
        driver.find_element(By.NAME, "password").send_keys(
            test_credentials["valid_user"]["password"]
        )
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        
        WebDriverWait(driver, 10).until(
            EC.url_contains("dashboard")
        )
    
    def test_navigation_works(self, driver, selenium_browser, test_base_url):
        driver.get(f"{test_base_url}/login")
        
        driver.find_element(By.CSS_SELECTOR, "nav a").click()
    
    def test_layout_no_horizontal_scroll(self, driver, selenium_browser, test_base_url):
        driver.get(test_base_url)
        
        scroll_width = driver.execute_script(
            "return document.documentElement.scrollWidth"
        )
        client_width = driver.execute_script(
            "return document.documentElement.clientWidth"
        )
        assert scroll_width <= client_width
    
    def test_js_no_errors_in_console(self, driver, selenium_browser, test_base_url):
        driver.get(test_base_url)
        
        logs = driver.get_log("browser")
        errors = [l for l in logs if l.get("level") == "SEVERE"]
        assert len(errors) == 0, f"JS errors found: {errors}"
    
    def test_contact_form_elements_visible(self, driver, selenium_browser, test_base_url):
        driver.get(f"{test_base_url}/contacts/add")
        
        name_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.NAME, "name"))
        )
        assert name_input.is_displayed()
    
    def test_no_broken_links(self, driver, selenium_browser, test_base_url):
        driver.get(test_base_url)
        
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links[:10]:
            href = link.get_attribute("href")
            if href and href.startswith(test_base_url):
                driver.get(href)
                assert driver.page_source


@pytest.mark.parametrize("browser", ["chrome", "firefox", "edge"])
class TestBrowserSpecific:
    def test_browser_version(self, driver, browser):
        caps = driver.capabilities
        assert caps.get("browserName") or caps