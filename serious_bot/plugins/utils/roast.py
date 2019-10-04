import requests
import random
from bs4 import BeautifulSoup


class Roast:
    def __init__(self):
        self.url = "http://www.gotlines.com/insults/{}"
        self.max_pages = 5

    def get_html(self, page=1):
        return requests.get(self.url.format(page)).text

    def parse_data(self, html):
        parser = BeautifulSoup(html, "html.parser")

        return parser.find_all("span", {"class": "linetext"})

    def get_random(self):
        random_page = random.randint(1, self.max_pages)
        html = self.get_html(random_page)

        _text_list = self.parse_data(html)

        return random.choice(_text_list).text
