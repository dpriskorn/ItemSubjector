from datetime import datetime
from typing import List

from pydantic import BaseModel

import config
from src.models.batch_job import BatchJob
from src.models.login import Login


class BatchJobs(BaseModel):
    jobs: List[BatchJob]

    @property
    def job_count(self):
        return len(self.jobs)

    def print_running_jobs(self):
        if not isinstance(self.jobs, list):
            raise ValueError("jobs is not a sparql_items")
        from src.helpers.console import console

        console.print(
            f"Running {len(self.jobs)} job(s) with a total of "
            f"{sum(len(job.main_subject_item.items.sparql_items) for job in self.jobs if job.main_subject_item.items and job.main_subject_item.items.sparql_items)} items "
            f"non-interactively now. You can take a "
            f"coffee break and lean back :)"
        )

    def run_jobs(self):
        from src.helpers.console import (
            console,
            print_keep_an_eye_on_wdqs_lag,
        )
        from src import print_finished

        if self.jobs is None or len(self.jobs) == 0:
            raise ValueError("did not get what we need")
        print_keep_an_eye_on_wdqs_lag()
        if config.login_instance is None:
            Login()
        self.print_running_jobs()
        start_time = datetime.now()
        for job in self.jobs:
            job.main_subject_item.add_to_items(jobs=self.jobs, job_count=self.job_count)
        print_finished()
        end_time = datetime.now()
        console.print(f"Total runtime: {end_time - start_time}")
