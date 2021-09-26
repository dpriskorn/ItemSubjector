from __future__ import annotations

from dataclasses import dataclass
from typing import List, TYPE_CHECKING

from models.task import Task

if TYPE_CHECKING:
    from models.suggestion import Suggestion


@dataclass
class BatchJob:
    """Models a batch job intended to be run non-interactively"""
    suggestion: Suggestion = None
    task: Task = None

    def run(self, jobs: List[BatchJob], job_count: int = None):
        if jobs is None:
            raise ValueError("jobs was None")
        if job_count is None:
            raise ValueError("job count was None")
        self.suggestion.add_to_items(task=self.task, jobs=jobs, job_count=job_count)
