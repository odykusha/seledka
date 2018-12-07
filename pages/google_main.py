
from selenium.webdriver.common.by import By

from ..elements.base import Page, Block, Element


class ResultBlocks(Block):
    title = Element.find_by_css_selector('.r a')


class GooglePage(Page):

    url = 'https://www.google.com.ua/'

    search_input = Element.find_by_name('q')
    result_list = ResultBlocks.as_list(By.CLASS_NAME, 'g')
    logo = Element.find_by_id('body')
