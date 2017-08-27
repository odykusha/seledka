# -*- coding: utf-8 -*-
class SoftException(Exception):
    pass


class SoftAssert(object):
    def check_assert_errors(self):
        if self.assert_errors != u'':
            print(self.assert_errors)
            raise SoftException

    def soft_assert_equal(self, current, excepted, message=None):
        if current != excepted:
            self.assert_errors += \
                u"*----------------- Soft Exception -------------------*\n" \
                u"Не совпадают значения \n" \
                u"\tтекущее: {current}\n" \
                u"\tожидаемое: {excepted}\n" \
                u"\tURL: {url}\n" \
                u"\t{message}\n\n".format(
                    current=current,
                    excepted=excepted,
                    url=self.driver.current_url,
                    message='message: ' + message if message else ''
                )
