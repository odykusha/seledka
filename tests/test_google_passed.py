import time
from selenium.webdriver.common.keys import Keys

from core import TestsCore

from pages.google_main import GooglePage


class PythonOrgSearch(TestsCore):

    def test_search_in_python_org(self):
        self.driver.get("https://www.google.com.ua/")
        self.assertIn("Python", self.driver.title)
        google_page = GooglePage(self.driver)
        google_page.search_input.send_keys("webdriver")
        google_page.search_input.send_keys(Keys.RETURN)
        time.sleep(1)

        self.assertEqual(
            len(google_page.result_list),
            10,
            u"query return not 10 results"
        )
