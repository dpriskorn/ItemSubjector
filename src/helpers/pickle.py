import os
import pickle
from typing import List

import config
from src.helpers.console import console
from src.models.batch_job import BatchJob


def add_to_pickle(job: BatchJob = None):
    if job is None:
        raise ValueError("Job was None")
    else:
        with open(config.pickle_file_path, 'ab') as file:
            pickle.dump(job, file, pickle.DEFAULT_PROTOCOL)


def read_from_pickle(path):
    with open(path, 'rb') as file:
        try:
            while True:
                yield pickle.load(file)
        except EOFError:
            pass


def check_if_pickle_exists():
    if os.path.exists(config.pickle_file_path):
        return True
    else:
        return False


def parse_pickle() -> List[BatchJob]:
    """Reads the pickle into a list of batch jobs"""
    if check_if_pickle_exists():
        jobs: List[BatchJob] = []
        for job in read_from_pickle(config.pickle_file_path):
            jobs.append(job)
        if len(jobs) == 0:
            console.print("No prepared jobs found")
        else:
            return jobs
    else:
        console.print("No pickle file found")


def remove_pickle():
    if os.path.exists(config.pickle_file_path):
        os.remove(config.pickle_file_path)
        console.print("The job list was removed")