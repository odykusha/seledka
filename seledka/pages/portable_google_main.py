
from seledka.elements import Page, Element


class DuckDuckGoPortablePage(Page):
    url = 'https://duckduckgo.com/'

    search_input = Element.find_by_id('search_form_input_homepage')
    result_lists = Element.find_all_by_css_selector("[data-nir]")
