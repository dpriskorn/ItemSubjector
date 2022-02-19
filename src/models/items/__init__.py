from __future__ import annotations

import random
from typing import List, TYPE_CHECKING, Optional

from pydantic import BaseModel

from src.models.task import Task
from src.models.wikimedia.wikidata.sparql_item import SparqlItem

if TYPE_CHECKING:
    from src.models.suggestion import Suggestion


class Items(BaseModel):
    list: Optional[List[SparqlItem]]

    def fetch_based_on_label(self,
                             suggestion: Suggestion = None,
                             task: Task = None):
        pass

    def random_shuffle_list(self):
        random.shuffle(self.list)
