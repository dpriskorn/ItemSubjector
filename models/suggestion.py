from pprint import pprint

import requests
from wikibaseintegrator.wbi_helpers import search_entities

import config
from helpers.console import console
from models.ngram import NGram
from models.wikidata import Item, EntityID


class Suggestion(Item):
    ngram: NGram = None

    def __init__(self,
                 id: str = None,
                 label: str = None,
                 description: str = None,
                 ngram: NGram = None):
        if id is not None:
            self.id = str(EntityID(id))
        self.label = label
        self.description = description
        self.ngram: NGram = ngram

    def __str__(self):
        """Return label and description, the latter cut to 50 chars"""
        return f"{self.label}: {self.description[:50]}..."