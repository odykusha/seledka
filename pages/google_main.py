# -*- coding: utf-8 -*-


class GooglePage(object):

    def __init__(self, driver):
        self.driver = driver

    @property
    def search_input(self):
        return self.driver.find_element_by_name("q")

    @property
    def result_list(self):
        return self.driver.find_elements_by_class_name('g')
