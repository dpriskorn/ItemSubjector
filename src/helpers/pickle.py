import os
import pickle
from typing import List

import config
from src.helpers.console import console
from src.models.batch_job import BatchJob


def add_to_job_pickle(job: BatchJob = None):
    if job is None:
        raise ValueError("Job was None")
    else:
        with open(config.job_pickle_file_path, 'ab') as file:
            pickle.dump(job, file, pickle.DEFAULT_PROTOCOL)


def add_to_main_subject_pickle(subjects: List[str] = None):
    with open(config.main_subjects_pickle_file_path, 'wb') as file:
        for qid in subjects:
            pickle.dump(qid, file, pickle.DEFAULT_PROTOCOL)


def read_from_pickle(path):
    with open(path, 'rb') as file:
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


def parse_job_pickle() -> List[BatchJob]:
    """Reads the pickle into a list of batch jobs"""
    if check_if_pickle_exists(config.job_pickle_file_path):
        jobs: List[BatchJob] = []
        for job in read_from_pickle(config.job_pickle_file_path):
            jobs.append(job)
        if len(jobs) == 0:
            console.print("No prepared jobs found")
        else:
            return jobs
    else:
        console.print("No pickle file found")


def parse_main_subjects_pickle() -> List[str]:
    """Reads the pickle into a list of main subjects"""
    if check_if_pickle_exists(config.main_subjects_pickle_file_path):
        subjects = []
        for subject in read_from_pickle(config.main_subjects_pickle_file_path):
            subjects.append(subject)
        if len(subjects) == 0:
            console.print("No qids found in the pickle.")
        else:
            # print(f"found:{subjects}")
            return subjects
    else:
        console.print("No main subjects pickle file found. "
                      "Create it by running 'python fetch_main_subjects.py'")
        exit(0)


def remove_pickle():
    if os.path.exists(config.job_pickle_file_path):
        os.remove(config.job_pickle_file_path)
        console.print("The job list was removed")