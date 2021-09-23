import os
import pickle
from typing import List

import config
from helpers.console import console
from models.batch_job import BatchJob


# Model of the pickle
# BatchJob
# BatchJob

# # load & show all stored objects
# for item in read_from_pickle(PICKLE_FILE):
#     print(repr(item))
# os.remove(PICKLE_FILE)

def add_to_pickle(job: BatchJob = None):
    if job is None:
        raise ValueError("Job was None")
    with open(config.pickle_file_path, 'ab') as file:
        pickle.dump(job, file, pickle.DEFAULT_PROTOCOL)


def read_from_pickle(path):
    with open(path, 'rb') as file:
        try:
            while True:
                yield pickle.load(file)
        except EOFError:
            pass


def parse_pickle() -> List[BatchJob]:
    """Reads the picle into a list of batch jobs"""
    if os.path.exists(config.pickle_file_path):
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