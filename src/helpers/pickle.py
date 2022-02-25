import hashlib
import os
import pickle
from typing import List, Optional

import config
from src.helpers.console import console
from src.models.batch_job import BatchJob

# TODO rewrite as OOP
from src.models.batch_jobs import BatchJobs


def add_to_job_pickle(job: BatchJob = None):
    if job is None:
        raise ValueError("Job was None")
    else:
        with open(config.job_pickle_file_path, "ab") as file:
            pickle.dump(job, file, pickle.DEFAULT_PROTOCOL)


def read_from_pickle(path):
    with open(path, "rb") as file:
        try:
            while True:
                yield pickle.load(file)
        except EOFError:
            pass


def check_if_pickle_exists(path):
    if os.path.exists(path):
        return True
    else:
        return False


def parse_job_pickle(silent: bool = False) -> Optional[BatchJobs]:
    """Reads the pickle into a list of batch jobs"""
    if check_if_pickle_exists(config.job_pickle_file_path):
        jobs: List[BatchJob] = []
        for job in read_from_pickle(config.job_pickle_file_path):
            jobs.append(job)
        if len(jobs) == 0:
            if not silent:
                console.print("No prepared jobs found")
            return None
        else:
            return BatchJobs(jobs=jobs)
    else:
        if not silent:
            console.print("No pickle file found")
        return None


def remove_job_pickle(silent: bool = False, hash: str = None):
    if hash is None:
        if os.path.exists(config.job_pickle_file_path):
            os.remove(config.job_pickle_file_path)
            if not silent:
                console.print("The job list file was removed")
    if os.path.exists(config.job_pickle_file_path):
        hash_now = get_hash_of_job_pickle()
        if hash == hash_now:
            os.remove(config.job_pickle_file_path)
            if not silent:
                console.print("The job list file was removed")
        else:
            console.print(
                "Job list file not deleted because the contents "
                "has changed since this batch of jobs was started."
            )
    else:
        console.print(
            f"Could not delete the job file. No file found at {config.job_pickle_file_path}"
        )


def get_hash_of_job_pickle():
    # inspired by https://codezup.com/python-program-calculate-hash-of-file-hashlib/
    block_size = 65536  # lets read stuff in 64kb chunks!
    hasher = hashlib.md5()
    with open(config.job_pickle_file_path, "rb") as file:
        buf = file.read(block_size)
        hasher.update(buf)
    # print(hasher.hexdigest())
    return hasher.hexdigest()
