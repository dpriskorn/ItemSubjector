import random
from typing import List

from pydantic import BaseModel

from src import Suggestion, Task
from src.models.wikimedia.wikidata.sparql_item import SparqlItem


class Items(BaseModel):
    list: List[SparqlItem]

    def fetch_based_on_label(self,
                             suggestion: Suggestion = None,
                             task: Task = None):
        pass

    def random_shuffle_list(self):
        random.shuffle(self.list)