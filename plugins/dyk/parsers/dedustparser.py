from .baseparser import BaseParser
import random

class DEDustParser(BaseParser):

    def __init__(self):
        self.name = 'Penrouk'

        loaded_file = open('./plugins/dyk/parsers/de_dust.txt', 'r')
        self.lines = loaded_file.readlines()
        loaded_file.close()

    def get_random(self):
        return random.choice(self.lines)
