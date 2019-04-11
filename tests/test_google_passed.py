
from ..core import WebTestCase

from ..pages.google_main import GooglePage


class PythonOrgSearch(WebTestCase):

    def test_search_webdriver_failed(self):
        """ проверка неработоспособного теста """
        google_page = GooglePage(self.driver)
        google_page.open()
        self.soft_assert_equal(
            "Python",
            self.driver.title
        )
        google_page.search_input.send_keys("webdriver").press_key()
        self.soft_assert_equal(
            len(google_page.result_lists),
            12,
            "query return not 10 results"
        )
        google_page.logo.wait_to_disappear()

    def test_search_webdriver_passed(self):
        """ проверка успешно проходимого теста """
        google_page = GooglePage(self.driver)
        google_page.open()
        google_page.search_input.send_keys("webdriver").press_key()
        google_page.result_lists.wait_to_display()
        self.soft_assert_page_title(
            "webdriver - Поиск в Google",
        )
        google_page.logo.wait_to_disappear()
