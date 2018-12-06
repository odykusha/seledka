# -*- coding: utf-8 -*-
from ..core import TestsCore

from ..pages.google_main import GooglePage


class PythonOrgSearch(TestsCore):

    def test_search_webdriver_failed(self):
        google_page = GooglePage(self.driver)
        google_page.open()
        self.soft_assert_equal(
            "Python",
            self.driver.title
        )
        google_page.search_input.send_keys("webdriver").send_keyword()
        self.soft_assert_equal(
            len(google_page.result_list),
            12,
            u"query return not 10 results"
        )

    def test_search_webdriver_passed(self):
        google_page = GooglePage(self.driver)
        google_page.open()
        google_page.search_input.send_keys("webdriver").send_keyword()
        self.soft_assert_equal(
            u"webdriver - Поиск в Google",
            self.driver.title
        )
