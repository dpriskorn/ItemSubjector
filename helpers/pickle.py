import os
import pickle
from pathlib import Path
from typing import List

import config
from helpers.console import console
from models.batch_job import BatchJob


# Model of the pickle
# BatchJob
# BatchJob

pickle_path = f"{Path.home()}/{config.pickle_file_path}"


def add_to_pickle(job: BatchJob = None):
    if job is None:
        raise ValueError("Job was None")
    with open(pickle_path, 'ab') as file:
        pickle.dump(job, file, pickle.DEFAULT_PROTOCOL)


def read_from_pickle(path):
    with open(path, 'rb') as file:
        try:
            while True:
                yield pickle.load(file)
        except EOFError:
            pass


def check_if_pickle_exists():
    if os.path.exists(pickle_path):
        return True
    else:
        return False


def parse_pickle() -> List[BatchJob]:
    """Reads the picle into a list of batch jobs"""
    if check_if_pickle_exists():
        jobs: List[BatchJob] = []
        for job in read_from_pickle(pickle_path):
            jobs.append(job)
        if len(jobs) == 0:
            console.print("No prepared jobs found")
        else:
            return jobs
    else:
        console.print("No pickle file found")


def remove_pickle():
    if os.path.exists(pickle_path):
        os.remove(pickle_path)
        console.print("The joblist was removed")
