from __future__ import annotations
from dataclasses import dataclass
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.suggestion import Suggestion
    from src.models.wikidata import Items


@dataclass
class BatchJob:
    """Models a batch job intended to be run non-interactively"""
    suggestion: Suggestion
    items: Items

    def run(self, jobs: List[BatchJob], job_count: int = None):
        if jobs is None:
            raise ValueError("jobs was None")
        if job_count is None:
            raise ValueError("job count was None")
        self.suggestion.add_to_items(items=self.items, jobs=jobs, job_count=job_count)
