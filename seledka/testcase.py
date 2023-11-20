
import os
import time
import unittest
import logging
import json
import requests

import allure
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options as ChromeOptions

from seledka.libs.retries import TryRequests
from seledka.exceptions import RequestSoftAssert, WebSoftAssert
from seledka.logger import check_console_error


log = logging.getLogger(__name__)


class WebTestCase(unittest.TestCase, WebSoftAssert):

    def setup_method(self, method):
        self.assert_errors = '\n'

        # browser_name = os.environ.get('BROWSER')
        capabilities = DesiredCapabilities.CHROME.copy()

        options = ChromeOptions()
        options.add_argument("--verbose")
        options.add_argument("--enable-logging --v=3")
        options.add_argument("--no-sandbox")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-gpu")
        if hasattr(method, 'portable'):
            options.add_experimental_option(
                "mobileEmulation",
                {'deviceName': 'Nexus 5'}
            )
        options.set_capability('cloud:options', capabilities)
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()

    def teardown_method(self, method):
        from datetime import datetime
        screen_path = '/tmp/screenshots_%s.png' % \
                      datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.driver.save_screenshot(screen_path)
        print('Test URL: %s' % self.driver.current_url)
        print('ScreenShot URL: %s' % screen_path)
        if os.environ.get('BROWSER') not in ['firefox', 'opera']:
            check_console_error(self.driver)
        if self.driver:
            self.driver.close()
        self.check_assert_errors()

    @property
    def log(self):
        """ логирование
        пример использования:
            self.log.info('---- some info -----')
            self.log.error('some shit')
            self.log.critical('Alarm dosn`t work')
        """
        return log

    def sleep(self, timeout=1):
        time.sleep(timeout)


# ----------------------------------------------------------------------------#
#                               REQUESTS
# ----------------------------------------------------------------------------#
class RequestTestCase(unittest.TestCase, RequestSoftAssert):

    session = requests.session()
    response = None

    def setup_method(self, method):
        self.assert_errors = '\n'

    def teardown_method(self, method):
        with allure.step('[close] Закрытие сессии'):
            if self.session:
                self.session.close()
        self.check_assert_errors()

    @TryRequests
    @allure.step('[Request] {url}')
    def make_request(
            self, url, method="GET", status_code=200,
            params=None, headers={}, data=None, cookies={}, **kwargs
    ):
        """ выполнение request запросов при тестировании API с логированием"""
        head_param = {"Api-Agent": "android"}
        head_param.update(headers)
        self.response = self.session.request(
            url=url,
            method=method,
            params=params,
            headers=head_param,
            data=data,
            verify=False,
            cookies=cookies,
            timeout=15,
            **kwargs
        )
        log.info(
            f"API[request]: \n"
            f"\tURL: {url} \n"
            f"\tMETHOD: {method} \n"
            f"\tPARAMS: {params} \n"
            f"\tHEADERS: {headers} \n"
            f"\tDATA: {data}"
        )

        self.soft_assert_equal(
            self.response.status_code,
            status_code,
            "Не совпадает код ответа request запроса"
        )

        try:
            _json = self.response.json()
        except Exception:
            _json = None

        allure.attach(
            json.dumps(_json, indent=4),
            name='[Response] {code} {reasone}, {seconds}sec'.format(
                code=self.response.status_code,
                reasone=self.response.reason,
                seconds=self.response.elapsed.total_seconds(),
            ),
            attachment_type=allure.attachment_type.JSON
        )
        log.info(
            "API[response]: \n"
            "\tCODE: {code}, {reason}, {seconds} sec\n"
            "\tJSON: \n{json}\n".format(
                code=self.response.status_code,
                reason=self.response.reason,
                seconds=self.response.elapsed.total_seconds(),
                json=json.dumps(_json, indent=4)
            )
        )
        # check_api_response(self)
        return self.response

    @property
    def log(self):
        """ логирование
        пример использования:
            self.log.info('---- some info -----')
            self.log.error('some shit')
            self.log.critical('Alarm dosn`t work')
        """
        return log
