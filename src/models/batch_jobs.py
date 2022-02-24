from datetime import datetime
from typing import List

from pydantic import BaseModel

from src.models.batch_job import BatchJob


class BatchJobs(BaseModel):
    jobs: List[BatchJob]

    @property
    def job_count(self):
        return len(self.jobs)

    def print_running_jobs(self):
        if not isinstance(self.jobs, list):
            raise ValueError("jobs is not a list")
        from src.helpers.console import console
        console.print(f"Running {len(self.jobs)} job(s) with a total of "
                      f"{sum(len(job.items.list) for job in self.jobs if job.items.list is not None)} items "
                      f"non-interactively now. You can take a "
                      f"coffee break and lean back :)")

    def run_jobs(self):
        from src.helpers.console import console, print_keep_an_eye_on_wdqs_lag, print_finished
        if self.jobs is None or len(self.jobs) == 0:
            raise ValueError("did not get what we need")
        print_keep_an_eye_on_wdqs_lag()
        from src import login
        login()
        self.print_running_jobs()
        start_time = datetime.now()
        for job in self.jobs:
            job.suggestion.add_to_items(items=job.items, jobs=self.jobs, job_count=self.job_count)
        print_finished()
        end_time = datetime.now()
        console.print(f'Total runtime: {end_time - start_time}')
