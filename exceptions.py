
class SoftAssert(object):
    def check_assert_errors(self):
        if self.assert_errors != '\n':
            raise AssertionError(self.assert_errors)

    def soft_assert_equal(self, current, excepted, message=None):
        if current != excepted:
            self.assert_errors += (
                f"*----------------- Soft Exception -------------------*\n"
                f"Не совпадают значения \n"
                f"\tТекущее: {current}\n"
                f"\tОжидаемое: {excepted}\n"
                f"\tURL: {self.driver.current_url}\n"
                f"\t{'Ошибка: ' + message if message else ''}\n\n"
            )
