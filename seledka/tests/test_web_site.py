
import pytest

from seledka.testcase import WebTestCase

from seledka.pages.google_main import GooglePage
from seledka.pages.portable_google_main import DuckDuckGoPortablePage


class PythonOrgSearch(WebTestCase):

    def test_search_google(self):
        """ проверка неработоспособного теста """
        google_page = GooglePage(self.driver)
        google_page.open()
        self.soft_assert_not_equal(
            "Python",
            self.driver.title
        )
        google_page.search_input.send_keys("webdriver").press_key()
        self.soft_assert_equal(
            len(google_page.result_lists),
            9,
            "query return not 10 results"
        )
        google_page.logo.wait_to_disappear()

    @pytest.mark.portable
    def test_search_duckduckgo_portable(self):
        """ проверка успешно проходимого теста """
        google_page = DuckDuckGoPortablePage(self.driver)
        google_page.open()
        google_page.search_input.send_keys("webdriver").press_key()
        self.soft_assert_equal(
            len(google_page.result_lists),
            10,
            "query return not 10 results"
        )
        self.soft_assert_page_title(
            "webdriver at DuckDuckGo",
        )
