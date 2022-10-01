from __future__ import annotations

import argparse
import random
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel

from src.models.task import Task
from src.models.wikimedia.wikidata.sparql_item import SparqlItem

if TYPE_CHECKING:
    from src.models.suggestion import Suggestion


class Items(BaseModel):
    list: Optional[List[SparqlItem]]

    @property
    def number_of_items(self):
        return len(self.list)

    def fetch_based_on_label(self, suggestion: Suggestion = None, task: Task = None):
        pass

    def random_shuffle_list(self):
        random.shuffle(self.list)

    def print_items_list(self, args: argparse.Namespace):
        from src import print_found_items_table

        print_found_items_table(args=args, items=self)
