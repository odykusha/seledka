
from selenium.webdriver.common.by import By

from ..elements.base import Page, Block, Element


class ResultBlocks(Block):
    title = Element(By.CSS_SELECTOR, '.r a')


class GooglePage(Page):

    url = 'https://www.google.com.ua/'

    search_input = Element(By.NAME, 'q')
    result_list = ResultBlocks.as_list(By.CLASS_NAME, 'g')
    logo = Element(By.ID, 'body')
