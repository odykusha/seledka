
import time
import logging
import collections
import allure

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    UnexpectedAlertPresentException,
)

from ..libs.screenshot import ScreenShots

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
        f'jQuery undefined (waiting time: {timeout} sec)'
    )


def find_elements(driver, by, locator, cycles=20):
    for i in range(cycles):
        elements = driver.find_elements(by, locator)
        if elements:
            return elements
        if i < (cycles - 1):
            time.sleep(0.5)
    else:
        raise ElementLocationException(f'Элемент {by}={locator} не найден')


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
        log.info(f'[SCROLL] coordinate: {element_coordinate}')


def _get_link_element(driver, text_link, index):
    """ Поиск ссылок """
    return find_elements(
        driver,
        By.XPATH,
        f"//a[contains(text(), '{text_link}')] | "
        f"//a//*[contains(text(), '{text_link}')]//.. | "
        f"//a[@title='{text_link}']"
    )[index]


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
            _ = obj.find_elements(self.by, self.locator)[self.index]  # noqa
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

    def take_part_screenshot(self):
        u""" Создать скриншот(частичный) элемента """
        screen_shot = ScreenShots(self.driver)
        screen_shot.take_part_screenshot(self.lookup())

        allure.attach(
            screen_shot.content,
            name=f'[скриншот] {{self.by}}={{self.locator}}',
            attachment_type=allure.attachment_type.PNG
        )
        log.warning(
            f'[скриншот] {screen_shot.url} {{self.by}}={{self.locator}}'
        )

    #                      find single elements (single)
    # ----------------------------------------------------------------------- #
    @classmethod
    def find_by_id(cls, value):
        return cls(By.ID, value)

    @classmethod
    def find_by_xpath(cls, value):
        return cls(By.XPATH, value)

    @classmethod
    def find_by_link_text(cls, value):
        return cls(By.LINK_TEXT, value)

    @classmethod
    def find_by_partial_link_text(cls, value):
        return cls(By.PARTIAL_LINK_TEXT, value)

    @classmethod
    def find_by_name(cls, value):
        return cls(By.NAME, value)

    @classmethod
    def find_by_tag_name(cls, value):
        return cls(By.TAG_NAME, value)

    @classmethod
    def find_by_class_name(cls, value):
        return cls(By.CLASS_NAME, value)

    @classmethod
    def find_by_css_selector(cls, value):
        return cls(By.CSS_SELECTOR, value)

    #                     find all elements (Sequence)
    # ----------------------------------------------------------------------- #
    @classmethod
    def find_all_by_id(cls, value):
        return cls.as_list(By.ID, value)

    @classmethod
    def find_all_by_xpath(cls, value):
        return cls.as_list(By.XPATH, value)

    @classmethod
    def find_all_by_link_text(cls, value):
        return cls.as_list(By.LINK_TEXT, value)

    @classmethod
    def find_all_by_partial_link_text(cls, value):
        return cls.as_list(By.PARTIAL_LINK_TEXT, value)

    @classmethod
    def find_all_by_name(cls, value):
        return cls.as_list(By.NAME, value)

    @classmethod
    def find_all_by_tag_name(cls, value):
        return cls.as_list(By.TAG_NAME, value)

    @classmethod
    def find_all_by_class_name(cls, value):
        return cls.as_list(By.CLASS_NAME, value)

    @classmethod
    def find_all_by_css_selector(cls, value):
        return cls.as_list(By.CSS_SELECTOR, value)


# --------------------------------------------------------------------------- #
#                                   PAGE
# --------------------------------------------------------------------------- #
class Page(object):

    def __init__(self, driver):
        self.driver = driver

    def open(self):
        with allure.step(f'open: {self.url}'):
            self.driver.get(self.url)

    def lookup(self):
        pass

    @allure.step("Переключение на вкладку {1}")
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

    def get_link(self, text_link, index=0):
        """ Поиск ссылки по названию либо по атрибуту 'title' """
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                f"//a[contains(text(), '{text_link}')] | "
                f"//a//*[contains(text(), '{text_link}')]//.. | "
                f"//a[@title='{text_link}']"
            ))
        )

        scroll_to_element(
            self.driver,
            _get_link_element(self.driver, text_link, index),
            with_offset=-55
        )
        link = _get_link_element(self.driver, text_link, index)
        ActionChains(self.driver).move_to_element_with_offset(
            link, 1, 1).perform()
        return link

    def take_screenshot(self):
        """ Создать скриншот страницы """
        screen_shot = ScreenShots(self.driver)
        screen_shot.take_screenshot()

        allure.attach(
            screen_shot.content,
            name=f'[скриншот] {self.driver.current_url}',
            attachment_type=allure.attachment_type.PNG
        )
        log.info(f'[скриншот] {screen_shot.url}')

    def accept_alert_popup(self):
        """Ожидание и закрытие всплывающего окна предупреждения
        js: alert()"""
        WebDriverWait(self.driver, 10).until(
            EC.alert_is_present(),
            "Не отображен алерт в течении 10сек"
        )
        self.driver.switch_to_alert().accept()


# --------------------------------------------------------------------------- #
#                                   Block
# --------------------------------------------------------------------------- #
class Block(Base):
    pass


# --------------------------------------------------------------------------- #
#                                  Element
# --------------------------------------------------------------------------- #
class Element(Base):

    def click(self, with_wait=True):
        """ Нажатие на элемент """
        if with_wait:
            self.wait_to_enabled()
        self.lookup().click()
        wait_for_page_loaded(self.driver)
        return self

    def clear(self):
        """ Ощищение текста в инпуте """
        self.click()
        self.lookup().send_keys(Keys.CONTROL + 'a')
        self.lookup().send_keys(Keys.BACKSPACE)
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

    def press_key(self, key='ENTER'):
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

    @allure.step('Переключение в фрейм')
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
def wait_load_page(driver, timeout=10):
    # wait full page load
    WebDriverWait(driver, timeout).until(
        lambda driver: driver.execute_script(
            "return document.readyState == 'complete'"),
        f'Page load timeout (waiting time: {timeout} sec)'
    )
    # enable_jquery(driver)
    if driver.execute_script('return !!window.jQuery == true;'):
        # wait ajax query
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.execute_script('return jQuery.active == 0;'),
            f'Ajax timeout (waiting time: {timeout} sec)'
        )
        # wait animation
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.execute_script(
                'return jQuery(":animated").length == 0;'),
            f'Animation timeout (waiting time: {timeout} sec)'
        )


def wait_for_page_loaded(driver):
    try:
        wait_load_page(driver)
    except UnexpectedAlertPresentException as e:
        log.warning(e)
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
