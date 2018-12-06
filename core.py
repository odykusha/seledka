# -*- coding: utf-8 -*-
import os
import platform
from datetime import datetime

import unittest
from selenium import webdriver

from .exceptions import SoftAssert


class TestsCore(unittest.TestCase, SoftAssert):

    def setUp(self):
        self.assert_errors = u'\n'
        # if platform.system() == 'Win32':
        chromedriver = "E:\instal\_Programming\chromedriver.exe"
        os.environ["webdriver.chrome.driver"] = chromedriver
        if platform.system() == 'Linux':
            chromedriver = "/usr/bin/chromedriver"
        self.driver = webdriver.Chrome(chromedriver)
        self.driver.maximize_window()

    def tearDown(self):
        screen_path = os.path.dirname(__file__) + '\\screenshots\\%s.png' % \
                      datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.driver.save_screenshot(screen_path)
        print('Test URL: %s' % self.driver.current_url)
        print('ScreenShot URL: %s' % screen_path)
        self.driver.close()
        self.check_assert_errors()
