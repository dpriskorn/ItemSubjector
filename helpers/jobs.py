import argparse
from datetime import datetime
from typing import Union, List

from helpers.cleaning import strip_prefix
from helpers.console import console, print_found_items_table, ask_add_to_job_queue, print_best_practice, \
    print_keep_an_eye_on_wdqs_lag, print_running_jobs, print_finished
from helpers.login import login
from helpers.pickle import add_to_pickle, check_if_pickle_exists, parse_pickle
from models.batch_job import BatchJob
from models.suggestion import Suggestion
from models.task import Task
from models.wikidata import Item


def do_job_preparation_or_run_directly(args: argparse.Namespace = None,
                                       jobs: List[BatchJob] = None):
    if args.prepare_jobs:
        if len(jobs) > 0:
            console.print(f"Adding {len(jobs)} job(s) to the jobs file")
            for job in jobs:
                add_to_pickle(job)
        if check_if_pickle_exists():
            jobs = parse_pickle()
            if len(jobs) > 0:
                console.print(f"The jobs list now contain a total of {len(jobs)} "
                              f"jobs with a total of "
                              f"{sum(len(job.task.items.list) for job in jobs)} items")
                console.print(f"You can run the jobs "
                              f"non-interactively e.g. on the Toolforge "
                              f"Kubernetes cluster using -r or --run-prepared-jobs. "
                              f"See https://phabricator.wikimedia.org/T285944 "
                              f"for details")
            else:
                raise ValueError("Pickle file had no jobs")
    else:
        run_jobs(jobs)


def process_qid_into_job(qid: str = None,
                         task: Task = None,
                         args: argparse.Namespace = None) -> Union[BatchJob, None]:
    # logger = logging.getLogger(__name__)
    if qid is None:
        raise ValueError("qid was None")
    if args is None:
        raise ValueError("args was None")
    if task is None:
        raise ValueError("task was None")
    qid = strip_prefix(qid)
    item = Item(
        id=qid,
        task=task
    )
    # TODO filter on the list instead of this
    if "protein " in item.label.lower() and args.match_existing_main_subjects:
        console.print("Skipping protein which is too hard to validate "
                      "given the information in the label and description")
        return None
    else:
        console.print(f"Working on {item}")
        # generate suggestion with all we need
        suggestion = Suggestion(
            item=item,
            args=args
        )
        with console.status(f'Fetching items with labels that have one of '
                            f'the search strings by running a total of '
                            f'{len(suggestion.search_strings)} queries on WDQS...'):
            task.items.fetch_based_on_label(suggestion=suggestion,
                                            task=task)
        if len(task.items.list) > 0:
            # Randomize the list
            task.items.random_shuffle_list()
            print_found_items_table(args=args,
                                    task=task)
            job = BatchJob(
                task=task,
                suggestion=suggestion
            )
            answer = ask_add_to_job_queue(job)
            if answer:
                return job
        else:
            console.print("No matching items found")


def process_user_supplied_qids_into_batch_jobs(args: argparse.Namespace = None,
                                               task: Task = None) -> List[BatchJob]:
    """Given a list of QIDs, we go through
    them and return a list of jobs"""
    # logger = logging.getLogger(__name__)
    if args is None:
        raise ValueError("args was None")
    if task is None:
        raise ValueError("task was None")
    print_best_practice(task)
    jobs = []
    for qid in args.add:
        job = process_qid_into_job(qid=qid,
                                   task=task,
                                   args=args)
        if job is not None:
            jobs.append(job)
    return jobs


def run_jobs(jobs):
    if jobs is None:
        raise ValueError("jobs was None")
    print_keep_an_eye_on_wdqs_lag()
    login()
    print_running_jobs(jobs)
    count = 0
    start_time = datetime.now()
    for job in jobs:
        count += 1
        job.run_add_job(jobs=jobs, job_count=count)
    print_finished()
    end_time = datetime.now()
    console.print(f'Total runtime: {end_time - start_time}')


