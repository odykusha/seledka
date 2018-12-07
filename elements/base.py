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
            f'Элемент {by}={locator} не найден'
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
    """ Прокрутка к элементу, если он выше границ экрана """
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
    parent = None
    page_object = []

    def bind(self, parent, driver):
        c = self.__class__.__new__(self.__class__)
        c.__dict__ = self.__dict__.copy()
        c.parent = parent
        c.driver = driver
        return c

    def __get__(self, instance, owner):
        # if 'Page' in str(instance.__class__.__bases__):
        #     if instance not in self.page_object:
        #         self.page_object.append(instance)
        #     else:
        #         self.page_object.remove(instance)
        #         self.page_object.append(instance)
        return self.bind(instance.lookup(), instance.driver)


class Base(Bindable):
    # driver = None
    index = 0

    def __init__(self, by, locator):
        self.by = by
        self.locator = locator

    def __len__(self):
        obj = self.parent if self.parent else self.driver
        return len(find_elements(obj, self.by, self.locator))

    @classmethod
    def as_list(cls, by, locator):
        return type(cls.__name__ + 'List', (cls, Sequence), {})(by, locator)

    def lookup(self):
        obj = self.parent if self.parent else self.driver
        WebDriverWait(self.driver, 15).until(
            lambda driver: len(
                find_elements(obj, self.by, self.locator)
            ) >= self.index + 1, 'Вышли за рамки индекса'
        )
        element = find_elements(obj, self.by, self.locator)[self.index]
        scroll_if_invisible(self.driver, element)
        return element

    @property
    def text(self):
        """ Возвращает весь текст в локаторе """
        return self.lookup().text

    def get_attribute(self, name):
        """Возвращает значение атрибута элемента
        :Args:
            name - название атрибута
        :пример:
            target_element.get_attribute("class")"""
        return self.lookup().get_attribute(name)

    def click(self):
        """ Нажатие на элемент """
        self.lookup().click()
        wait_for_page_loaded(self.driver)
        # return self

    def is_present(self):
        """ Проверка что элемент находится в ДОМе """
        obj = self.parent if self.parent else self.driver
        try:
            _ = obj.find_elements(self.by, self.locator)[self.index]
            return True
        except (NoSuchElementException, IndexError):
            return False

    def is_displayed(self):
        """ Проверка что элемент отображен на странице """
        obj = self.parent if self.parent else self.driver
        try:
            element = obj.find_elements(self.by, self.locator)[self.index]
            return element.is_displayed()
        except (NoSuchElementException, IndexError):
            return False

    def wait_to_present(self, timeout=5):
        """ Ожидание пока элемент не появистя в ДОМе """
        WebDriverWait(self.driver, timeout).until(
            lambda driver: self.is_present(),
            f"Элемент {self.by}={self.locator} не отобразился в "
            f"течении {timeout}сек."
        )
        wait_for_page_loaded(self.driver)
        return self

    def wait_to_display(self, timeout=5):
        """ Ожидание пока элемент не отобразится на странице """
        WebDriverWait(self.driver, timeout).until(
            lambda driver: self.is_displayed(),
            f"Элемент {self.by}={self.locator} найден в ДОМе, "
            f"но не отображен в течении {timeout}сек."
        )
        wait_for_page_loaded(self.driver)
        return self

    def wait_to_disappear(self, timeout=5):
        """ Ожидание пока не исчезнет элемент """
        WebDriverWait(self.driver, timeout).until(
            EC.invisibility_of_element_located((
                (self.by, self.locator)
            )),
            f"Элемент {self.by}={self.locator} не исчез после {timeout}сек."
        )

    def hover_over(self):
        """ имитация "наведения" указателя на элемент """
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
        pass

    def switch_to_window(self, window_index=0, timeout=10):
        """ Ожидаем окно и переключаемся в него """
        # wait
        WebDriverWait(self.driver, timeout).until(
            EC.number_of_windows_to_be((
                    window_index + 1
            )),
            f"Не появилось окно с индексом: '{window_index}' "
            f"[всего вкладок: {len(self.driver.window_handles)}]"
        )
        # switch
        self.driver.switch_to.window(
            self.driver.window_handles[window_index]
        )


# --------------------------------------------------------------------------- #
#                                   Block
# --------------------------------------------------------------------------- #
class Block(Base):
    @classmethod
    def find_by_id(cls, value):
        return Block(By.ID, value)

    @classmethod
    def find_by_xpath(cls, value):
        return Block(By.XPATH, value)

    @classmethod
    def find_by_link_text(cls, value):
        return Block(By.LINK_TEXT, value)

    @classmethod
    def find_by_partial_link_text(cls, value):
        return Block(By.PARTIAL_LINK_TEXT, value)

    @classmethod
    def find_by_name(cls, value):
        return Block(By.NAME, value)

    @classmethod
    def find_by_tag_name(cls, value):
        return Block(By.TAG_NAME, value)

    @classmethod
    def find_by_class_name(cls, value):
        return Base(By.CLASS_NAME, value)

    @classmethod
    def find_by_css_selector(cls, value):
        return Base(By.CSS_SELECTOR, value)


# --------------------------------------------------------------------------- #
#                                  Element
# --------------------------------------------------------------------------- #
class Element(Base):

    # def click(self, with_wait=True):
    #     """ Нажатие на элемент """
    #     if with_wait:
    #         self.wait_to_enabled()
    #     self.lookup().click(self)
    #     # wait_for_page_loaded(self.driver)
    #     return self

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

    def clear(self):
        """ Ощищение текста в инпуте """
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
        """ Проверка что элемент выбран.
        Работает для: чекбоксов и радиобатонов """
        return self.lookup().is_selected()

    def is_enabled(self):
        """ Проверка что элемент доступен для работы """
        webdriver_element = False
        if self.get_attribute("disabled") is None:
            # "is None" бывает в том случае если нет атрибута: 'disabled',
            # т.е. элемент является *enabled*
            webdriver_element = True
        return self.lookup().is_enabled() and webdriver_element

    def is_disabled(self):
        """ Проверка что элемент НЕдоступен для работы """
        return not self.is_enabled()

    def send_keys(self, *value):
        """ Отправка текста в инпут. Автоматически ощищает поле, перед вводом
        Используется так же для загрузки файлов:
            *.send_keys('/tmp/some_document.doc')
        """
        self.lookup()
        self.wait_to_display()
        try:
            self.clear()
        except Exception as e:
            log.critical(f'EXCEPTION in send_keys: {e}')
        self.lookup().send_keys(*value)
        return self

    def send_only_keys(self, *value):
        """ отправка только текста, без очистки """
        self.lookup().send_keys(*value)

    def send_fast(self, value, with_action=True):
        """заполняем инпуты с помощью JS’а в React формы"""
        self.lookup()
        self.wait_to_display()
        script_click = """
            var elem = arguments[0];
            elem.click();"""
        self.driver.execute_script(script_click, self.lookup())

        script_send = """
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
        """ передача эмуляции нажатия клавиш selenium.Keys() """
        keyword = getattr(Keys, key)
        if key != 'ESCAPE':
            self.click()
        self.lookup().send_keys(keyword)

    def wait_for_text_present(self, text):
        u""" Ожидание появления текста в элементе """
        WebDriverWait(self.driver, 30).until(
            EC.text_to_be_present_in_element(
                (self.by, self.locator), text
            ), f"Text: {text}, не появился в течении 30 сек."
        )

    def wait_attribute_value(self, attribute_name, attribute_value):
        """ Ожидание появления в атрибуте элемента(attribute_name)
        значения(attribute_value) """
        WebDriverWait(self.driver, 10).until(
            lambda driver: attribute_value == self.get_attribute(
                attribute_name),
            f"Значение атрибута {{attribute_name}}={{attribute_value}} "
            f"не изменилось"
        )

    def wait_to_enabled(self, timeout=5):
        """ Ожидание пока элемент станет доступен для взаимодейтсвия """
        self.lookup()
        WebDriverWait(self.driver, timeout).until(
            lambda driver: self.is_enabled(),
            f"Элемент {{self.by}}={{self.locator}} не стал enable спустя "
            f"{timeout}сек."
        )
        return self

    def wait_to_disabled(self, timeout=5):
        """ Ожидание пока элемент станет НЕ! доступен для взаимодейтсвия """
        self.lookup()
        WebDriverWait(self.driver, timeout).until(
            lambda driver: not self.is_enabled(),
            f"Элемент {{self.by}}={{self.locator}} не стал disabled спустя "
            f"{timeout}сек."

        )
        return self

    def switch_to_frame(self, timeout=5):
        """ Ожидаем фрейм и переключаемся в него """
        WebDriverWait(self.driver, timeout).until(
            EC.frame_to_be_available_and_switch_to_it((
                self.lookup()
            )), "Не переключились в фрейм"
        )


# --------------------------------------------------------------------------- #
#                                Page load waits
# --------------------------------------------------------------------------- #
def enable_jquery(driver, timeout=5):
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
        f'jQuery undefined (waiting time: {timeout} sec)'
    )


def wait_load_page(driver, timeout=10):
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
