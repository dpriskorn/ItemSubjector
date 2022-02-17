import random
from typing import List

from src.models.wikidata.item import Item


class Items:
    list: List[Item] = []

    def fetch_based_on_label(self):
        pass

    def random_shuffle_list(self):
        random.shuffle(self.list)
