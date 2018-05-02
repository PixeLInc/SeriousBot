from .baseparser import BaseParser
from bs4 import BeautifulSoup
import random
import requests


class DJTechParser(BaseParser):

    def __init__(self):
        self.name = 'DJTech'

    def get_random(self):
        html = requests.get('http://www.djtech.net/humor/shorty_useless_facts.htm').text

        parser = BeautifulSoup(html, 'html.parser')

        text_list = parser.find_all('font', {'style': 'font-size: 11pt'})

        if len(text_list) > 0:
            return random.choice(text_list).text.replace("\n\t\t", "")
        else:
            return None
