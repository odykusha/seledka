
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
            len(google_page.result_lists),
            12,
            "query return not 10 results"
        )
        google_page.logo.wait_to_disappear()

    def test_search_webdriver_passed(self):
        google_page = GooglePage(self.driver)
        google_page.open()
        google_page.search_input.send_keys("webdriver").send_keyword()
        google_page.result_lists.wait_to_display()
        self.soft_assert_equal(
            "webdriver - Поиск в Google",
            self.driver.title
        )
        google_page.logo.wait_to_disappear()
