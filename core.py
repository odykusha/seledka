import os
import sys
import unittest
from datetime import datetime

from selenium import webdriver


# class AssertionError(Exception):
#     def __init__(self, message, errors):
#         super(AssertionError, self).__init__(message)
#         self.errors = errors

class TestsCore(unittest.TestCase):

    def setUp(self):
        chromedriver = "E:\instal\_Programming\chromedriver.exe"
        os.environ["webdriver.chrome.driver"] = chromedriver
        self.driver = webdriver.Chrome(chromedriver)

    def tearDown(self):
        screen_path = os.path.dirname(__file__) + '\\screenshots\\%s.png' % datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.driver.save_screenshot(screen_path)
        print('Test URL: %s' % self.driver.current_url)
        print('ScreenShot URL: %s', screen_path)
        print(sys.exc_info())
        self.driver.close()
