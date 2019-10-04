from .parsers import dykparser
from .parsers import djtechparser
from .parsers import dedustparser

import random

PARSERS = [
    dykparser.DYKParser(),
    djtechparser.DJTechParser(),
    dedustparser.DEDustParser(),
]


def grab_fact():
    parser = random.choice(PARSERS)

    print(f"Using {parser.name}")

    fact = parser.get_random()
    if fact is None:
        return ("Failed to grab a fact!", None)
    else:
        return (fact, parser.name)
