
import os
import datetime
import requests
from PIL import Image
from io import BytesIO

from seledka.libs.retries import TryRequests


SCREEENSHOT_HOST = 'https://screenshots.dev/'


class ScreenShots(object):

    _driver = None
    _img_path = None        # /tmp/screenshot_27_12_25_17_477984.png  <file>
    _img_name = None        # screenshot_27_12_25_17_477984.png       <name>

    url = None  # https://screenshots.dev/screenshot_27_12_25_17_477984.png
    content = None          # <base64>

    def __init__(self, driver=None):
        self._driver = driver

    def __get_screenshot_path(self, name="screenshot"):
        """ создание пути и имени будущего скриншота """
        now = datetime.datetime.now().strftime('%d_%H_%M_%S_%f')
        img_folder = "/tmp"
        self._img_name = f"{name}_{now}.png"
        if not os.path.exists(img_folder):
            os.makedirs(img_folder)
        self._img_path = os.path.join(img_folder, self._img_name)

    def __set_scroll_windows_size(self):
        """ Расширение экрана до максимально возможного """
        window_width = self._driver.execute_script(
            "return document.documentElement.scrollWidth"
        )
        window_height = self._driver.execute_script(
            "return document.documentElement.scrollHeight"
        )
        self._driver.set_window_size(
            max(1920, window_width),
            max(1080, window_height),
        )

    def __add_screen_border(self):
        """ Добавления границы видимости экрана в момент прогона теста """
        script = """
            var height = window.innerHeight - 5;
            var width = window.innerWidth - 25;
            var p_top = window.pageYOffset;
            var p_left = window.pageXOffset + 5;

            var div = document.createElement('div');
            div.id = "border_for_screenshot";
            div.style = "border: 2px dashed #0015ff; top: " + p_top + "px; left: " + p_left + "px; height: " + height + "px; width: " + width + "px; position: fixed;";

            document.body.insertBefore(div, document.body.firstChild); """

        if os.getenv('VAGGAOPT_GRID'):
            self._driver.execute_script(script)

    def __remove_screen_border(self):
        u""" Удаление границы видимости экрана в момент прогона теста """
        from seledka.elements.base import enable_jquery
        enable_jquery(self._driver)
        script = """
            var div = jQuery('#border_for_screenshot')[0];
            div.remove(); """

        if os.getenv('VAGGAOPT_GRID'):
            self._driver.execute_script(script)

    def __upload_img(self):
        """ Загрузка скриншота на сервер """
        try:
            with open(self._img_path) as open_file:
                self.content = open_file.read()

            def read_in_chunks(img, block_size=1024, chunks=-1):
                """ Lazy function (generator) to read a file piece by piece.
                Default chunk size: 1k. """
                while chunks:
                    data = img.read(block_size)
                    if not data:
                        break
                    yield data
                    chunks -= 1

            self.url = SCREEENSHOT_HOST + self._img_name
            upload_file = requests.request(
                url=self.url,
                method='PUT',
                auth=('selenium', 'selenium'),
                data=read_in_chunks(open(self._img_path, 'rb')),
                verify=False,
                timeout=5
            )
            os.remove(self._img_path)

            if upload_file.status_code != 201:
                self.url = (
                    f'[ERROR]: {upload_file.status_code}, {upload_file.reason}'
                )

        except Exception as e:
            self.url = f'No take screenshot: {repr(e)}'

    @classmethod
    @TryRequests
    def get_screen_png(cls, screen_url):
        """ Содержимое скриншота(base64) """
        return requests.request(
            url=screen_url,
            method='GET',
            verify=False
        ).content

    def take_screenshot(self):
        """ Формирование Полного скриншота """
        self.__get_screenshot_path()
        self.__add_screen_border()
        self.__set_scroll_windows_size()
        self._driver.save_screenshot(self._img_path)
        self.__upload_img()
        self.__remove_screen_border()
        return self

    def take_part_screenshot(self, element):
        """ Формирование Частичного скриншота(элмемента, блока) """
        # if not os.getenv('VAGGAOPT_GRID'):
        #     return 'test not run in grid'

        self.__get_screenshot_path()
        self.__set_scroll_windows_size()
        png = self._driver.get_screenshot_as_png()

        script = "return arguments[0].getBoundingClientRect();"
        element_coordinate = self._driver.execute_script(script, element)

        im = Image.open(BytesIO(png))
        im = im.crop((
            int(element_coordinate['left'] - 2),
            int(element_coordinate['top'] - 2),
            int(element_coordinate['right'] + 3),
            int(element_coordinate['bottom'] + 2)
        ))
        im.save(self._img_path)
        im.close()
        self.__upload_img()
        return self

    def take_screen_by_url(self, url):
        """ Формирование скриншота по урлу(для писем) """
        # открываем новую вкладку и переходим в нее
        self._driver.execute_script("window.open('');")
        self._driver.switch_to.window(
            self._driver.window_handles[-1]
        )
        # переходим по урлу, делаем скриншет
        self._driver.get(url, with_logs=False)
        self.take_screenshot()
        # закрываем вкладку, переходим в начальную позицию
        self._driver.close()
        self._driver.switch_to.window(
            self._driver.window_handles[-1]
        )
        return self
