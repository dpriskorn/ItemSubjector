import argparse
from dataclasses import dataclass

from models.suggestion import Suggestion
from models.task import Task
from models.wikidata import Items


@dataclass
class BatchJob:
    """Models a batch job intended to be run non-interactively"""
    suggestion: Suggestion
    items: Items

    def run(self):
        self.suggestion.add_to_items(items=self.items)
