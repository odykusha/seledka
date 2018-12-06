# -*- coding: utf-8 -*-

from ..elements.base import Page, Element


class GooglePage(Page):

    url = 'https://www.google.com.ua/'

    search_input = Element.find_by_name('q')
    result_list = Element.find_by_class_name('g')
