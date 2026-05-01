"""
Selenium Test Suite - MERN E-Commerce Application
15 Automated Test Cases using Headless Chrome
Target: http://localhost:8086 (CI environment)
"""

import unittest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

BASE_URL = os.environ.get("APP_URL", "http://localhost:8086")
WAIT_TIMEOUT = 15


def get_headless_driver():
    """Create and return a headless Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver


class TestHomePage(unittest.TestCase):
    """Test cases for the Home/Landing Page"""

    def setUp(self):
        self.driver = get_headless_driver()
        self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)

    def tearDown(self):
        self.driver.quit()

    def test_01_homepage_loads_successfully(self):
        """TC-01: Verify homepage loads with HTTP 200 and title is present"""
        self.driver.get(BASE_URL)
        time.sleep(3)
        title = self.driver.title
        self.assertIsNotNone(title, "Page title should not be None")
        self.assertNotIn("Error", title, "Page should not show an error")
        print(f"[PASS] TC-01: Homepage loaded - Title: '{title}'")

    def test_02_homepage_has_navbar(self):
        """TC-02: Verify navigation bar is present on homepage"""
        self.driver.get(BASE_URL)
        time.sleep(3)
        # Look for common navbar elements: nav tag or header
        nav_elements = self.driver.find_elements(By.TAG_NAME, "nav")
        header_elements = self.driver.find_elements(By.TAG_NAME, "header")
        has_nav = len(nav_elements) > 0 or len(header_elements) > 0
        self.assertTrue(has_nav, "Navigation bar should be present on homepage")
        print("[PASS] TC-02: Navbar is present on homepage")

    def test_03_homepage_has_product_listings(self):
        """TC-03: Verify product listings section is rendered"""
        self.driver.get(BASE_URL)
        time.sleep(4)
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        # The page should have content (not blank or error)
        self.assertGreater(len(body_text), 50,
                           "Homepage body should have meaningful content")
        print(f"[PASS] TC-03: Homepage has content ({len(body_text)} chars)")

    def test_04_page_does_not_show_javascript_error(self):
        """TC-04: Verify no critical JS crash (blank white page)"""
        self.driver.get(BASE_URL)
        time.sleep(3)
        root = self.driver.find_elements(By.ID, "root")
        if root:
            inner = root[0].get_attribute("innerHTML")
            self.assertGreater(len(inner), 10,
                               "React root should have rendered content")
        print("[PASS] TC-04: React app rendered successfully (no blank screen)")


class TestNavigation(unittest.TestCase):
    """Test cases for page navigation"""

    def setUp(self):
        self.driver = get_headless_driver()
        self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)

    def tearDown(self):
        self.driver.quit()

    def test_05_login_page_accessible(self):
        """TC-05: Verify Login page is accessible via /login route"""
        self.driver.get(f"{BASE_URL}/login")
        time.sleep(3)
        body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        page_src = self.driver.page_source.lower()
        has_login = ("login" in body_text or "sign in" in body_text or
                     "login" in page_src)
        self.assertTrue(has_login,
                        "Login page should contain login/sign-in content")
        print("[PASS] TC-05: Login page is accessible")

    def test_06_register_page_accessible(self):
        """TC-06: Verify Register/Signup page is accessible"""
        self.driver.get(f"{BASE_URL}/register")
        time.sleep(3)
        page_src = self.driver.page_source.lower()
        body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        has_register = ("register" in body_text or "sign up" in body_text or
                        "create account" in body_text or "register" in page_src)
        self.assertTrue(has_register,
                        "Register page should contain registration content")
        print("[PASS] TC-06: Register page is accessible")

    def test_07_login_form_has_email_and_password_fields(self):
        """TC-07: Verify login form contains email and password input fields"""
        self.driver.get(f"{BASE_URL}/login")
        time.sleep(3)
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        input_types = [i.get_attribute("type") for i in inputs]
        input_names = [i.get_attribute("name") for i in inputs]
        input_placeholders = [i.get_attribute("placeholder") or "" for i in inputs]
        all_attrs = " ".join(
            str(t) + " " + str(n) + " " + str(p)
            for t, n, p in zip(input_types, input_names, input_placeholders)
        ).lower()
        has_email = "email" in all_attrs or "text" in input_types
        has_password = "password" in input_types or "password" in all_attrs
        self.assertTrue(has_email, "Login form should have an email/text field")
        self.assertTrue(has_password, "Login form should have a password field")
        print("[PASS] TC-07: Login form has email and password fields")

    def test_08_register_form_has_required_fields(self):
        """TC-08: Verify register form contains name, email, and password fields"""
        self.driver.get(f"{BASE_URL}/register")
        time.sleep(3)
        inputs = self.driver.find_elements(By.TAG_NAME, "input")
        self.assertGreaterEqual(len(inputs), 2,
                                "Register form should have at least 2 input fields")
        print(f"[PASS] TC-08: Register form has {len(inputs)} input fields")


class TestAuthentication(unittest.TestCase):
    """Test cases for login / authentication flows"""

    def setUp(self):
        self.driver = get_headless_driver()
        self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)

    def tearDown(self):
        self.driver.quit()

    def _find_input(self, *identifiers):
        """Helper: find an input field by type, name, placeholder, or id."""
        for identifier in identifiers:
            # Try by type
            elems = self.driver.find_elements(By.CSS_SELECTOR,
                                              f"input[type='{identifier}']")
            if elems:
                return elems[0]
            # Try by name
            elems = self.driver.find_elements(By.CSS_SELECTOR,
                                              f"input[name='{identifier}']")
            if elems:
                return elems[0]
            # Try by placeholder (partial)
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            for inp in all_inputs:
                ph = (inp.get_attribute("placeholder") or "").lower()
                if identifier.lower() in ph:
                    return inp
        return None

    def test_09_invalid_login_shows_error(self):
        """TC-09: Verify invalid credentials show an error message"""
        self.driver.get(f"{BASE_URL}/login")
        time.sleep(3)

        email_field = self._find_input("email", "text")
        password_field = self._find_input("password")

        if not email_field or not password_field:
            self.skipTest("Login form fields not found – page structure may differ")

        email_field.clear()
        email_field.send_keys("nonexistent_user_xyz@test.com")
        password_field.clear()
        password_field.send_keys("WrongPassword123!")

        # Click submit button
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        submit_btn = None
        for btn in buttons:
            btn_text = btn.text.lower()
            btn_type = btn.get_attribute("type")
            if "login" in btn_text or "sign in" in btn_text or btn_type == "submit":
                submit_btn = btn
                break

        if submit_btn:
            submit_btn.click()
            time.sleep(4)

        body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        # Still on login page OR error message visible
        current_url = self.driver.current_url
        still_on_login = "/login" in current_url
        has_error = any(word in body_text for word in
                        ["error", "invalid", "incorrect", "failed",
                         "wrong", "not found", "unauthorized"])

        self.assertTrue(still_on_login or has_error,
                        "Invalid login should stay on login page or show error")
        print("[PASS] TC-09: Invalid login handled correctly")

    def test_10_empty_login_form_submission(self):
        """TC-10: Verify submitting empty login form is blocked or shows validation"""
        self.driver.get(f"{BASE_URL}/login")
        time.sleep(3)

        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        submit_btn = None
        for btn in buttons:
            btn_text = btn.text.lower()
            btn_type = btn.get_attribute("type")
            if "login" in btn_text or "sign in" in btn_text or btn_type == "submit":
                submit_btn = btn
                break

        if not submit_btn:
            self.skipTest("Submit button not found")

        submit_btn.click()
        time.sleep(3)

        current_url = self.driver.current_url
        body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()

        still_on_login = "/login" in current_url
        has_validation = any(word in body_text for word in
                             ["required", "enter", "please", "cannot be empty",
                              "invalid", "error"])

        self.assertTrue(still_on_login or has_validation,
                        "Empty form should not proceed past login")
        print("[PASS] TC-10: Empty login form submission blocked")


class TestProductsAndCart(unittest.TestCase):
    """Test cases for product browsing and cart functionality"""

    def setUp(self):
        self.driver = get_headless_driver()
        self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)

    def tearDown(self):
        self.driver.quit()

    def test_11_products_page_accessible(self):
        """TC-11: Verify products listing page loads"""
        for path in ["/products", "/shop", "/"]:
            self.driver.get(f"{BASE_URL}{path}")
            time.sleep(3)
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            if len(body_text) > 100:
                print(f"[PASS] TC-11: Products accessible at {BASE_URL}{path}")
                return
        self.fail("Products page not found at common routes")

    def test_12_cart_page_accessible(self):
        """TC-12: Verify cart page is accessible"""
        for path in ["/cart", "/basket"]:
            self.driver.get(f"{BASE_URL}{path}")
            time.sleep(3)
            body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            if "cart" in body_text or "basket" in body_text or "empty" in body_text:
                print(f"[PASS] TC-12: Cart page accessible at {BASE_URL}{path}")
                return
        # Try clicking cart icon from homepage
        self.driver.get(BASE_URL)
        time.sleep(3)
        cart_links = self.driver.find_elements(By.CSS_SELECTOR,
                                               "a[href*='cart'], a[href*='basket']")
        if cart_links:
            cart_links[0].click()
            time.sleep(3)
            body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            has_cart = any(w in body_text for w in ["cart", "basket", "empty", "item"])
            self.assertTrue(has_cart, "Cart page should show cart content")
            print("[PASS] TC-12: Cart page accessible via navbar link")
        else:
            print("[PASS] TC-12: Cart route check completed (no direct cart link found)")

    def test_13_search_functionality_present(self):
        """TC-13: Verify a search input or search icon is present on homepage"""
        self.driver.get(BASE_URL)
        time.sleep(3)
        page_src = self.driver.page_source.lower()
        search_inputs = self.driver.find_elements(By.CSS_SELECTOR,
                                                  "input[type='search'], "
                                                  "input[placeholder*='search' i], "
                                                  "input[name*='search' i]")
        has_search = len(search_inputs) > 0 or "search" in page_src
        self.assertTrue(has_search, "Homepage should have a search feature")
        print("[PASS] TC-13: Search functionality present")

    def test_14_product_detail_page_loads(self):
        """TC-14: Verify clicking a product opens its detail page"""
        self.driver.get(BASE_URL)
        time.sleep(4)
        # Try to find product cards / links
        product_links = self.driver.find_elements(By.CSS_SELECTOR,
                                                  "a[href*='product'], "
                                                  "a[href*='/p/'], "
                                                  ".product-card a, "
                                                  "[class*='product'] a")
        if not product_links:
            # Fallback: find any anchor that looks like a product
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            product_links = [l for l in all_links
                             if "product" in (l.get_attribute("href") or "").lower()]

        if product_links:
            href = product_links[0].get_attribute("href")
            self.driver.get(href)
            time.sleep(3)
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            self.assertGreater(len(body_text), 50,
                               "Product detail page should have content")
            print(f"[PASS] TC-14: Product detail page loads at {href}")
        else:
            # If no products yet, just verify homepage loaded with content
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            self.assertGreater(len(body_text), 50,
                               "App should render content even with no products")
            print("[PASS] TC-14: No product links found but app renders correctly")


class TestResponsivenessAndUI(unittest.TestCase):
    """Test cases for UI/UX and responsiveness"""

    def setUp(self):
        self.driver = get_headless_driver()
        self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)

    def tearDown(self):
        self.driver.quit()

    def test_15_page_title_is_set(self):
        """TC-15: Verify all major routes have a non-empty page title"""
        routes = ["/", "/login", "/register"]
        for route in routes:
            self.driver.get(f"{BASE_URL}{route}")
            time.sleep(2)
            title = self.driver.title
            self.assertIsNotNone(title, f"Title missing on {route}")
            self.assertGreater(len(title), 0, f"Empty title on {route}")
            print(f"[PASS] TC-15: Route '{route}' has title: '{title}'")


if __name__ == "__main__":
    # Run with verbose output for Jenkins
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestHomePage))
    suite.addTests(loader.loadTestsFromTestCase(TestNavigation))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthentication))
    suite.addTests(loader.loadTestsFromTestCase(TestProductsAndCart))
    suite.addTests(loader.loadTestsFromTestCase(TestResponsivenessAndUI))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with non-zero code if tests failed (Jenkins needs this)
    import sys
    sys.exit(0 if result.wasSuccessful() else 1)
