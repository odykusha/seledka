
import allure

# from .libs.screenshot import ScreenShots


class BaseSoftAssert(object):
    def check_assert_errors(self):
        if self.assert_errors != '\n':
            raise AssertionError(self.assert_errors)

    def add_failed_info(self, msg, error):
        with allure.step(f'[SoftAssertion]: {msg}'):
            # if hasattr(self, 'driver'):
            #     allure.attach(
            #         ScreenShots(self.driver).take_screenshot().content,
            #         name=self.driver.current_url,
            #         attachment_type=allure.attachment_type.PNG
            #     )
            allure.attach(
                error,
                name='В чём ошибка',
                attachment_type=allure.attachment_type.JSON
            )
            if msg:
                error += f"\t{'Примечание: ' + msg}\n"
            self.assert_errors += (error + self.base_msg())

    def soft_assert_equal(self, current, excepted, message=None):
        if current != excepted:
            error = (
                f"*-------- Soft Assertion (Не совпадают значения) --------*\n"
                f"\tТекущее: '{current}'\n"
                f"\tОжидаемое: '{excepted}'\n"
            )
            self.add_failed_info(message, error)

    def soft_assert_in(self, member, container, message=None):
        """ Проверка что member находится в container(Частичное вхождение) """
        if member not in container:
            error = (
                f"*------- Soft Assertion (Нет частичного вхождения) ------*\n"
                f"\t'{member}' отсутствует в '{container}'\n"
            )
            self.add_failed_info(message, error)


class WebSoftAssert(BaseSoftAssert):

    def base_msg(self):
        return (
            f"\turl: {self.driver.current_url}\n"
            f"\tScreenshot - ..skip..\n\n"
            # ScreenShots(self.driver).take_screenshot().url
        )

    def soft_assert_page_title(
            self, expected_title, msg="Не правильный заголовок странички"
    ):
        """ Проверка названия заголовка страницы """
        self.soft_assert_equal(self.driver.title, expected_title, msg)

    def soft_assert_current_url(
            self, expected_url, msg="Не правильный текущий url"
    ):
        """ Проверка url текущей страницы """
        self.soft_assert_equal(self.driver.current_url, expected_url, msg)

    def soft_assert_current_url_contains(
            self, url_mask, msg='Не правильный шаблон в url'
    ):
        """ Проверка частичного наименования url текущей страницы """
        self.soft_assert_in(url_mask, self.driver.current_url, msg)


class RequestSoftAssert(BaseSoftAssert):

    @property
    def url(self):
        try:
            return self.response.url
        except Exception:
            return ''

    def base_msg(self):
        return f"\turl: {self.url}\n\n"
