
import os
import time
import platform
import unittest
import logging

from selenium import webdriver

from .exceptions import SoftAssert

log = logging.getLogger(__name__)


class TestsCore(unittest.TestCase, SoftAssert):

    def setUp(self):
        self.assert_errors = '\n'

        if platform.system() == 'Win32':
            chromedriver = "E:\instal\_Programming\chromedriver.exe"
            # os.environ["webdriver.chrome.driver"] = chromedriver
            # self.driver = webdriver.Chrome(chromedriver)
        if platform.system() == 'Linux':
            chromedriver = "/usr/bin/chromedriver"
            os.environ["webdriver.chrome.driver"] = chromedriver
            self.driver = webdriver.Chrome(chromedriver)
        if platform.system() == 'Darwin':
            self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    def tearDown(self):
        # from datetime import datetime
        # screen_path = os.path.dirname(__file__) + '\\screenshots\\%s.png' % \
        #               datetime.now().strftime("%Y-%m-%d_%H%M%S")
        # self.driver.save_screenshot(screen_path)
        # print('Test URL: %s' % self.driver.current_url)
        # print('ScreenShot URL: %s' % screen_path)
        if self.driver:
            self.driver.close()
        self.check_assert_errors()

    @property
    def log(self):
        return log

    def sleep(self, timeout=1):
        time.sleep(timeout)
