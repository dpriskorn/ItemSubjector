from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, TYPE_CHECKING

from models.task import Task

if TYPE_CHECKING:
    from models.suggestion import Suggestion
    from models.deletion_target import DeletionTarget


@dataclass
class BatchJob:
    """Models a batch job intended to be run non-interactively"""
    suggestion: Suggestion = None
    target: DeletionTarget = None
    task: Task = None

    def __str__(self):
        return (f"suggestion:{self.suggestion}\n"
                f"target:{self.target}\n"
                f"task:{self.task}")

    def run_add_job(self,
                    jobs: List[BatchJob] = None,
                    job_count: int = None):
        logger = logging.getLogger(__name__)
        if jobs is None:
            raise ValueError("jobs was None")
        if job_count is None:
            raise ValueError("job count was None")
        if self.task is None:
            raise ValueError("self.task was None")
        logger.debug(f"suggestion:{self.suggestion}")
        logger.debug(f"self.task:{self.task}")
        self.suggestion.add_to_items(task=self.task, jobs=jobs, job_count=job_count)

    def run_delete_job(self,
                       jobs: List[BatchJob] = None,
                       job_count: int = None):
        if self.target is None:
            raise ValueError("self.target was None")
        if jobs is None:
            raise ValueError("jobs was None")
        if job_count is None:
            raise ValueError("job count was None")
        self.target.delete_from_items(task=self.task, jobs=jobs, job_count=job_count)
