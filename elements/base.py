# -*- coding: utf-8 -*-
import time
import logging
import collections
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    UnexpectedAlertPresentException,
)


log = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
#                              Global functions
# --------------------------------------------------------------------------- #
def enable_jquery(driver, timeout=15):
    # enable_jquery
    driver.execute_script("""
            jqueryUrl = 'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js';
            if (typeof jQuery == 'undefined') {
                var script = document.createElement('script');
                var head = document.getElementsByTagName('head')[0];
                var done = false;
                script.onload = script.onreadystatechange = (function() {
                    if (!done && (!this.readyState || this.readyState == 'loaded'
                            || this.readyState == 'complete')) {
                        done = true;
                        script.onload = script.onreadystatechange = null;
                        head.removeChild(script);

                    }
                });
                script.src = jqueryUrl;
                head.appendChild(script);
            };""")
    # wait ajax
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script(
            'return typeof jQuery != "undefined"'
        ),
        'jQuery undefined (waiting time: %s sec)' % timeout
    )


def find_elements(driver, by, locator, cycles=20):
    for i in range(cycles):
        elements = driver.find_elements(by, locator)
        if elements:
            return elements
        if i < (cycles - 1):
            time.sleep(0.5)
    else:
        raise ElementLocationException(
            u'Элемент {%s=%s} не найден' % (by, locator)
        )


def scroll_to_element(driver, element, with_offset=0, inside_element=None):
    enable_jquery(driver)
    if not inside_element:
        script = """
            var elem = arguments[0];
            jQuery('html, body').animate({
                scrollTop: jQuery(elem).offset().top + arguments[1]
                }, 'fast', null
            );
                """
    else:
        script = """
            var elem = arguments[0];
            var inside = arguments[2];
            var posArray = jQuery(elem).position();
            jQuery(inside).animate({scrollTop: posArray.top}, 'fast', null);
                 """
    # wait_for_page_loaded(driver)
    driver.execute_script(script, element, with_offset, inside_element)


def scroll_if_invisible(driver, element):
    u""" Прокрутка к элементу, если он выше границ экрана """
    script = """return arguments[0].getBoundingClientRect();"""
    element_coordinate = driver.execute_script(script, element)
    if element_coordinate['bottom'] < 0:
        scroll_to_element(driver, element, with_offset=-60)
        log.info('[SCROLL] coordinate: %s' % element_coordinate)


# --------------------------------------------------------------------------- #
#                                  CORE
# --------------------------------------------------------------------------- #
class Sequence(collections.Sequence):

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __getitem__(self, val):
        if isinstance(val, slice):
            start = val.start or 0
            stop = val.stop or len(self)
            step = val.step or 1
            return (self[i] for i in range(start, stop, step))
        else:
            c = self.bind(self.parent, self.driver)
            c.index = val
            return c

    def find(self, by, locator):
        c = self.bind(self.parent, self.driver)
        c.by = by
        c.locator = locator
        return c


class Bindable(object):

    def bind(self, parent, driver, parent_cls=None):
        c = self.__class__.__new__(self.__class__)
        c.__dict__ = self.__dict__.copy()
        c.parent = parent
        c.parent_cls = parent_cls
        c.driver = driver
        return c

    def __get__(self, instance, owner):
        return self.bind(instance.lookup(), instance.driver, instance)


class Base(Bindable):

    def __init__(self, by, locator):
        self.by = by
        self.locator = locator
        self.index = 0

    def __len__(self):
        obj = self.parent if self.parent else self.driver
        return len(find_elements(obj, self.by, self.locator))

    def lookup(self):
        obj = self.parent if self.parent else self.driver
        WebDriverWait(self.driver, 15).until(
            lambda driver: len(
                find_elements(obj, self.by, self.locator)
            ) >= self.index + 1, u'Вышли за рамки индекса'
        )
        element = find_elements(obj, self.by, self.locator)[self.index]
        scroll_if_invisible(self.driver, element)
        return element

    @property
    def text(self):
        u""" Возвращает весь текст в локаторе """
        return self.lookup().text

    def get_attribute(self, name):
        """Возвращает значение атрибута элемента
        :Args:
            name - название атрибута
        :пример:
            target_element.get_attribute("class")"""
        return self.lookup().get_attribute(name)

    def click(self):
        u""" Нажатие на элемент """
        self.lookup().click()
        wait_for_page_loaded(self.driver)
        # return self

    def is_present(self):
        u""" Проверка что элемент находится в ДОМе """
        obj = self.parent if self.parent else self.driver
        try:
            _ = obj.find_elements(self.by, self.locator)[self.index]
            return True
        except (NoSuchElementException, IndexError):
            return False

    def is_displayed(self):
        u""" Проверка что элемент отображен на странице """
        obj = self.parent if self.parent else self.driver
        try:
            element = obj.find_elements(self.by, self.locator)[self.index]
            return element.is_displayed()
        except (NoSuchElementException, IndexError):
            return False

    def wait_to_present(self, timeout=30):
        u""" Ожидание пока элемент не появистя в ДОМе """
        WebDriverWait(self.driver, timeout).until(
            lambda driver: self.is_present(),
            u"Элемент {%s=%s} не отобразился в течении %s секунд"
            % (self.by, self.locator, timeout)
        )
        wait_for_page_loaded(self.driver)
        return self

    def wait_to_display(self, timeout=30):
        u""" Ожидание пока элемент не отобразится на странице """
        WebDriverWait(self.driver, timeout).until(
            lambda driver: self.is_displayed(),
            u"Элемент {%s=%s} найден в ДОМе, "
            u"но не отображен в течении %s сек"
            % (self.by, self.locator, timeout)
        )
        wait_for_page_loaded(self.driver)
        return self

    def wait_to_disappear(self, timeout=30):
        u""" Ожидание пока не исчезнет элемент """
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((
                (self.by, self.locator)
            )), u"Элемент {%s=%s} не исчез после %s сек" % (
                self.by, self.locator, timeout)
        )

    def hover_over(self):
        u""" имитация "наведения" указателя на элемент """
        scroll_to_element(self.driver, self.lookup(), with_offset=-60)
        ActionChains(self.driver).move_to_element(self.lookup()).perform()
        return self


# --------------------------------------------------------------------------- #
#                                   PAGE
# --------------------------------------------------------------------------- #
class Page(object):
    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(self.url)

    def lookup(self):
        return None

    def switch_to_window(self, window_index=0, timeout=30):
        u""" Ожидаем окно и переключаемся в него """
        # wait
        WebDriverWait(self.driver, timeout).until(
            EC.number_of_windows_to_be((
                    window_index + 1
            )), u"Не появилось окно с индексом: '%s' [всего вкладок: %s]"
                % (window_index, len(self.driver.window_handles))
        )
        # switch
        self.driver.switch_to.window(
            self.driver.window_handles[window_index]
        )


# --------------------------------------------------------------------------- #
#                                   Block
# --------------------------------------------------------------------------- #
class Block(Base):
    pass


# --------------------------------------------------------------------------- #
#                                  Element
# --------------------------------------------------------------------------- #
class Element(Base):

    def __init__(self, by, locator):
        Base.__init__(self, by, locator)

    # --- find --- #
    @classmethod
    def find_by_id(cls, value):
        return Element(By.ID, value)

    @classmethod
    def find_by_xpath(cls, value):
        return Element(By.XPATH, value)

    @classmethod
    def find_by_link_text(cls, value):
        return Element(By.LINK_TEXT, value)

    @classmethod
    def find_by_partial_link_text(cls, value):
        return Element(By.PARTIAL_LINK_TEXT, value)

    @classmethod
    def find_by_name(cls, value):
        return Element(By.NAME, value)

    @classmethod
    def find_by_tag_name(cls, value):
        return Element(By.TAG_NAME, value)

    @classmethod
    def find_by_class_name(cls, value):
        return Element(By.CLASS_NAME, value)

    @classmethod
    def find_by_css_selector(cls, value):
        return Element(By.CSS_SELECTOR, value)
    # --- find --- #

    # def click(self, with_wait=True):
    #     u""" Нажатие на элемент """
    #     if with_wait:
    #         self.wait_to_enabled()
    #     self.lookup().click(self)
    #     # wait_for_page_loaded(self.driver)
    #     return self

    def clear(self):
        u""" Ощищение текста в инпуте """
        self.click()
        # from first symbol
        ActionChains(self.driver).\
            key_down(Keys.END). \
            perform()
        # mark to last symbol
        ActionChains(self.driver).\
            key_down(Keys.CONTROL).\
            key_down(Keys.SHIFT).\
            key_down(Keys.HOME).\
            key_up(Keys.CONTROL).\
            key_up(Keys.SHIFT).\
            perform()
        # send BACKSPACE
        ActionChains(self.driver).\
            key_down(Keys.BACKSPACE).\
            perform()
        return self

    def is_selected(self):
        u""" Проверка что элемент выбран.
        Работает для: чекбоксов и радиобатонов """
        return self.lookup().is_selected()

    def is_enabled(self):
        u""" Проверка что элемент доступен для работы """
        webdriver_element = False
        if self.get_attribute("disabled") is None:
            # "is None" бывает в том случае если нет атрибута: 'disabled',
            # т.е. элемент является *enabled*
            webdriver_element = True
        return self.lookup().is_enabled() and webdriver_element

    def is_disabled(self):
        u""" Проверка что элемент НЕдоступен для работы """
        return not self.is_enabled()

    def send_keys(self, *value):
        u""" Отправка текста в инпут. Автоматически ощищает поле, перед вводом
        Используется так же для загрузки файлов:
            *.send_keys('/tmp/some_document.doc')
        """
        self.lookup()
        self.wait_to_display()
        try:
            self.clear()
        except Exception as e:
            log.critical(u'EXCEPTION in send_keys: %s' % e)
        self.lookup().send_keys(*value)
        return self

    def send_only_keys(self, *value):
        u""" отправка только текста, без ощистки """
        self.lookup().send_keys(*value)

    def send_fast(self, value, with_action=True):
        u"""заполняем инпуты с помощью JS’а в React формы"""
        self.lookup()
        self.wait_to_display()
        script_click = u"""
            var elem = arguments[0];
            elem.click();"""
        self.driver.execute_script(script_click, self.lookup())

        script_send = u"""
            var my_event = new Event('input', { bubbles: true });
            var elem = arguments[0];
            elem.value = `%s`;
            elem.dispatchEvent(my_event);""" % value
        self.driver.execute_script(script_send, self.lookup())
        # add action
        if with_action:
            self.send_only_keys('0')
            ActionChains(self.driver). \
                key_down(Keys.BACKSPACE). \
                perform()

    def send_keyword(self, key='ENTER'):
        u""" передача эмуляции нажатия клавиш selenium.Keys() """
        keyword = getattr(Keys, key)
        if key != 'ESCAPE':
            self.click()
        self.lookup().send_keys(keyword)

    def wait_for_text_present(self, text):
        u""" Ожидание появления текста в элементе """
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (self.by, self.locator), text
            ), u"Text: {%s}, не появился в течении 30 сек." % text
        )

    def wait_attribute_value(self, attribute_name, attribute_value):
        u""" Ожидание появления в атрибуте элемента(attribute_name)
        значения(attribute_value) """
        WebDriverWait(self.driver, 10).until(
            lambda driver: attribute_value == self.get_attribute(
                attribute_name),
            u"Значение атрибута {%s}={%s} не изменилось" %
            (attribute_name, attribute_value)
        )

    def wait_to_enabled(self, timeout=30):
        u""" Ожидание пока элемент станет доступен для взаимодейтсвия """
        self.lookup()
        WebDriverWait(self.driver, timeout).until(
            lambda driver: self.is_enabled(),
            u"Элемент {%s}={%s} не стал enable спустя %sсек." %
            (self.by, self.locator, timeout)
        )
        return self

    def wait_to_disabled(self, timeout=10):
        u""" Ожидание пока элемент станет НЕ! доступен для взаимодейтсвия """
        self.lookup()
        WebDriverWait(self.driver, timeout).until(
            lambda driver: not self.is_enabled(),
            u"Элемент {%s}={%s} не стал disabled спустя %sсек." %
            (self.by, self.locator, timeout)
        )
        return self

    def switch_to_frame(self, timeout=15):
        u""" Ожидаем фрейм и переключаемся в него """
        WebDriverWait(self.driver, timeout).until(
            EC.frame_to_be_available_and_switch_to_it((
                self.lookup()
            )), u"Не переключились в фрейм"
        )


# --------------------------------------------------------------------------- #
#                                Page load waits
# --------------------------------------------------------------------------- #
def enable_jquery(driver, timeout=15):
    # enable_jquery
    driver.execute_script("""
            jqueryUrl = 'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js';
            if (typeof jQuery == 'undefined') {
                var script = document.createElement('script');
                var head = document.getElementsByTagName('head')[0];
                var done = false;
                script.onload = script.onreadystatechange = (function() {
                    if (!done && (!this.readyState || this.readyState == 'loaded'
                            || this.readyState == 'complete')) {
                        done = true;
                        script.onload = script.onreadystatechange = null;
                        head.removeChild(script);

                    }
                });
                script.src = jqueryUrl;
                head.appendChild(script);
            };""")
    # wait ajax
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script(
            'return typeof jQuery != "undefined"'
        ),
        'jQuery undefined (waiting time: %s sec)' % timeout
    )


def wait_load_page(driver, timeout=30):
    # wait full page load
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script(
            "return document.readyState == 'complete'"),
        'Page load timeout (waiting time: %s sec)' % timeout
    )
    if driver.execute_script('return !!window.jQuery == true;'):
        # wait ajax query
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.execute_script('return jQuery.active == 0;'),
            'Ajax timeout (waiting time: %s sec)' % timeout
        )
        # wait animation
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.execute_script(
                'return jQuery(":animated").length == 0;'
            ), 'Animation timeout (waiting time: %s sec)' % timeout
        )


def wait_for_page_loaded(driver):
    try:
        wait_load_page(driver)
        # wait_to_diasppear_spinner(driver)

    except UnexpectedAlertPresentException as e:
        alert_is_present = EC.alert_is_present()
        if alert_is_present(driver):
            driver.switch_to_alert().accept()
            # alert = driver.switch_to_alert()
            # e.alert_text = alert.text
            # alert.dismiss()
        # raise e


# --------------------------------------------------------------------------- #
#                                Exceptions
# --------------------------------------------------------------------------- #
class ElementLocationException(Exception):
    pass
