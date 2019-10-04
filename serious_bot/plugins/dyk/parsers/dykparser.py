from .baseparser import BaseParser
from bs4 import BeautifulSoup
import random
import requests


class DYKParser(BaseParser):
    def __init__(self):
        self.name = "Did-You-Knows"

    def get_random(self):
        page = random.randint(1, 50)

        html = requests.get(f"http://www.did-you-knows.com/?page={page}").text
        parser = BeautifulSoup(html, "html.parser")

        text_list = parser.find_all("span", {"class": "dykText"})

        if len(text_list) > 0:
            return "Did you know " + random.choice(text_list).text
        else:
            return None
