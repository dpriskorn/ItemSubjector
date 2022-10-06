# from __future__ import annotations

import argparse
import logging
import random
from typing import Any, List

from pydantic import BaseModel

from src.helpers.console import console
from src.models.wikimedia.wikidata.item.sparql import SparqlItem

# if TYPE_CHECKING:
#     from src.models.wikimedia.wikidata.item.main_subject import MainSubjectItem

logger = logging.getLogger(__name__)


class Items(BaseModel):
    # pydantic forwardref error
    main_subject_item: Any  # type MainSubjectItem
    sparql_items: List[SparqlItem] = []

    @property
    def number_of_sparql_items(self):
        return len(self.sparql_items)

    def fetch_based_on_label(self):
        pass

    def random_shuffle_items(self):
        random.shuffle(self.sparql_items)

    def print_items_list(self, args: argparse.Namespace):
        from src import print_found_items_table

        print_found_items_table(args=args, items=self)

    def remove_duplicates(self):
        if self.sparql_items is None:
            raise ValueError("items.sparql_items was None")
        logger.debug(f"{len(self.sparql_items)} before duplicate removal")
        self.sparql_items = list(set(self.sparql_items))
        logger.debug(f"{len(self.sparql_items)} after duplicate removal")

    def print_total_items(self):
        console.print(f"Got a total of {len(self.sparql_items)} items")

    def execute_queries(self):
        pass
