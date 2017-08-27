# -*- coding: utf-8 -*-
import time
from selenium.webdriver.common.keys import Keys

from core import TestsCore

from pages.google_main import GooglePage


class PythonOrgSearch(TestsCore):

    def test_search_webdriver_failed(self):
        self.driver.get("https://www.google.com.ua/")
        self.soft_assert_equal("Python", self.driver.title)
        google_page = GooglePage(self.driver)
        google_page.search_input.send_keys("webdriver")
        google_page.search_input.send_keys(Keys.RETURN)
        time.sleep(1)

        self.soft_assert_equal(
            len(google_page.result_list),
            12,
            u"query return not 10 results"
        )

    def test_search_webdriver_passed(self):
        self.driver.get("https://www.google.com.ua/")
        google_page = GooglePage(self.driver)
        google_page.search_input.send_keys("webdriver")
        google_page.search_input.send_keys(Keys.RETURN)
        self.soft_assert_equal(
            u"webdriver - Поиск в Google",
            self.driver.title
        )
