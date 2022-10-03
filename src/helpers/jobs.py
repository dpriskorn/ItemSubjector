from __future__ import annotations

import argparse
import logging
import random
from typing import List

import config
from src.helpers.cli_messages import (
    print_best_practice,
    print_job_statistics,
)
from src.helpers.console import console
from src.helpers.menus import select_task
from src.helpers.questions import (
    ask_add_to_job_queue,
    ask_yes_no_question,
)
from src.models.batch_job import BatchJob
from src.models.batch_jobs import BatchJobs
from src.models.wikimedia.wikidata.item.main_subject import MainSubjectItem
from src.tasks import Task

# TODO rewrite as OOP
logger = logging.getLogger(__name__)


def process_user_supplied_qids_into_batch_jobs(
    args: argparse.Namespace = None, task: Task = None
) -> List[BatchJob]:
    """Given a sparql_items of QIDs, we go through
    them and return a sparql_items of jobs"""
    # logger = logging.getLogger(__name__)
    if not args:
        raise ValueError("args was None")
    if not task:
        raise ValueError("task was None")
    print_best_practice(task)
    jobs = []
    for qid in args.add:
        main_subject_item = MainSubjectItem(qid=qid, args=args, task=task)
        job = main_subject_item.fetch_items_and_get_job()
        if job:
            jobs.append(job)
    return jobs


def handle_job_preparation_or_run_directly_if_any_jobs(
    args: argparse.Namespace = None, batchjobs: BatchJobs = None
):
    if batchjobs is None:
        raise ValueError("batchjobs was None")
    if args is None:
        raise ValueError("args was None")
    if len(batchjobs.jobs) > 0:
        if args.prepare_jobs:
            console.print(f"Adding {len(batchjobs.jobs)} job(s) " f"to the jobs file")
            for job in batchjobs.jobs:
                from src import add_to_job_pickle

                add_to_job_pickle(job)
            print_job_statistics(batchjobs=batchjobs)
            console.print(
                f"You can run the jobs "
                f"non-interactively e.g. on the Toolforge "
                f"Kubernetes cluster using -r or --run-prepared-jobs. "
                f"See Kubernetes_HOWTO.md for details."
            )
        else:
            batchjobs.run_jobs()


def get_validated_main_subjects_as_jobs(
    args: argparse.Namespace, main_subjects: List[str]
) -> BatchJobs:
    """This function randomly picks a subject and add it to the
    sparql_items of jobs if it had any matches and the user approved it"""
    if args is None:
        raise ValueError("args was None")
    if main_subjects is None:
        raise ValueError("main subjects was None")
    qid_subjects_not_picked_yet = main_subjects
    task: Task = select_task()
    if task is None:
        raise ValueError("Got no task")
    if not isinstance(task, Task):
        raise ValueError("task was not a Task object")
    batchjobs = BatchJobs(jobs=[])
    while True:
        # Check if we have any subjects left in the sparql_items
        if len(qid_subjects_not_picked_yet):
            console.print(f"Picking a random main subject")
            qid = random.choice(qid_subjects_not_picked_yet)
            qid_subjects_not_picked_yet.remove(qid)
            main_subject_item = MainSubjectItem(
                qid=qid, args=args, task=task, confirmation=args.no_confirmation
            )
            job = main_subject_item.fetch_items_and_get_job()
            if job:
                # Here we check if the user has enabled no ask more limit.
                if args.no_ask_match_more_limit is None:
                    logger.debug("No ask more was None")
                    if job.main_subject_item.items:
                        job.main_subject_item.items.print_items_list(args=args)
                        job.main_subject_item.print_search_strings()
                        answer = ask_add_to_job_queue(job)
                        if answer:
                            batchjobs.jobs.append(job)
                else:
                    batchjobs.jobs.append(job)
            logger.debug(f"joblist now has {len(batchjobs.jobs)} jobs")
            print_job_statistics(batchjobs=batchjobs)
            if len(qid_subjects_not_picked_yet) > 0:
                if (
                    args.no_ask_match_more_limit is None
                    or args.no_ask_match_more_limit
                    < sum(
                        len(job.main_subject_item.items.sparql_items)
                        for job in batchjobs.jobs
                        if job.main_subject_item.items
                        and job.main_subject_item.items.sparql_items
                    )
                ):
                    answer_was_yes = ask_yes_no_question("Match one more?")
                    if not answer_was_yes:
                        break
            else:
                console.print("No more subjects in the sparql_items.")
                break
        else:
            console.print("No more subjects in the sparql_items. Exiting.")
            break
    if args.no_ask_match_more_limit:
        batchjobs_limit = BatchJobs(jobs=[])
        for job in batchjobs.jobs:
            if job.main_subject_item.items:
                job.main_subject_item.items.print_items_list(args=args)
                job.main_subject_item.print_search_strings()
                if (
                    config.automatically_approve_jobs_with_less_than_fifty_matches
                    and job.main_subject_item.items.number_of_sparql_items < 50
                ):
                    console.print(
                        f"This job with {job.main_subject_item.items.number_of_sparql_items} matching items was automatically approved",
                        style="green",
                    )
                    batchjobs_limit.jobs.append(job)
                else:
                    answer = ask_add_to_job_queue(job)
                    if answer:
                        batchjobs_limit.jobs.append(job)
        return batchjobs_limit
    return batchjobs
