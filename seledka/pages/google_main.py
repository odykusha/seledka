
from seledka.elements import Page, Block, Element


class ResultBlocks(Block):
    title = Element.find_by_css_selector('.r a')


class GooglePage(Page):

    url = 'https://www.google.com.ua/'

    search_input = Element.find_by_name('q')
    result_lists = ResultBlocks.find_all_by_class_name('g')
    logo = Element.find_by_id('body')
