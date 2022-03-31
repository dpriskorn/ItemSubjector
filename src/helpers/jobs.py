from __future__ import annotations

import argparse
import logging
import random
from typing import Union, List, TYPE_CHECKING, Optional

import config
from src import (
    strip_prefix,
    print_best_practice,
    console,
    ask_yes_no_question,
    TaskIds,
    ask_add_to_job_queue,
    print_job_statistics,
)
from src.helpers.menus import select_task
from src.models.batch_jobs import BatchJobs
from src.models.items import Items
from src.models.items.academic_journals import AcademicJournalItems
from src.models.items.riksdagen_documents import RiksdagenDocumentItems
from src.models.items.scholarly_articles import ScholarlyArticleItems
from src.models.items.thesis import ThesisItems
from src.tasks import Task

if TYPE_CHECKING:
    from src import Task, BatchJob

# TODO rewrite as OOP
logger = logging.getLogger(__name__)


def process_qid_into_job(
    qid: str = None,
    task: Task = None,
    args: argparse.Namespace = None,
    confirmation: bool = False,
) -> Union[BatchJob, None]:
    if qid is None:
        raise ValueError("qid was None")
    if args is None:
        raise ValueError("args was None")
    if task is None:
        raise ValueError("task was None")
    from src.models.wikimedia.wikidata.item import Item

    item = Item(
        id=strip_prefix(qid),
    )
    item.fetch_label_and_description_and_aliases(task=task)
    if item.label is not None:
        console.print(f"Working on {item}")
        # generate suggestion with all we need
        from src import Suggestion

        suggestion = Suggestion(item=item, task=task, args=args)
        if confirmation:
            answer = ask_yes_no_question("Do you want to continue?")
            if not answer:
                return None
        suggestion.extract_search_strings()
        if config.loglevel == logging.INFO:
            suggestion.print_search_strings()
        if suggestion.search_strings is None:
            raise ValueError("suggestion.search_strings was None")
        number_of_queries = (
            len(suggestion.search_strings) * task.number_of_queries_per_search_string
        )
        with console.status(
            f"Fetching items with labels that have one of "
            f"the search strings by running a total of "
            f"{number_of_queries} "
            f"queries on WDQS..."
        ):
            items: Optional[Items] = None
            if task.id == TaskIds.SCHOLARLY_ARTICLES:
                items = ScholarlyArticleItems()
            elif task.id == TaskIds.RIKSDAGEN_DOCUMENTS:
                items = RiksdagenDocumentItems()
            elif task.id == TaskIds.THESIS:
                items = ThesisItems()
            elif task.id == TaskIds.ACADEMIC_JOURNALS:
                items = AcademicJournalItems()
            else:
                raise ValueError(f"{task.id} was not recognized")
            items.fetch_based_on_label(suggestion=suggestion, task=task)
        if items.list is None:
            raise ValueError("items.list was None")
        if len(items.list) > 0:
            # Remove duplicates
            logger.debug(f"{len(items.list)} before duplicate removal")
            items.list = list(set(items.list))
            logger.debug(f"{len(items.list)} after duplicate removal")
            # Randomize the list
            items.random_shuffle_list()
            from src import BatchJob

            job = BatchJob(
                items=items, number_of_queries=number_of_queries, suggestion=suggestion
            )
            return job
        else:
            console.print("No matching items found")
            return None
    else:
        console.print(
            f"Label for {task.language_code} was None on {item.url()}, skipping"
        )
        return None


def process_user_supplied_qids_into_batch_jobs(
    args: argparse.Namespace = None, task: Task = None
) -> List[BatchJob]:
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
        job = process_qid_into_job(qid=qid, task=task, args=args)
        if job is not None:
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
    args: argparse.Namespace = None, main_subjects: List[str] = None
) -> BatchJobs:
    """This function randomly picks a subject and present it for validation"""
    if args is None:
        raise ValueError("args was None")
    if main_subjects is None:
        raise ValueError("main subjects was None")
    subjects_not_picked_yet = main_subjects
    task: Task = select_task()
    if task is None:
        raise ValueError("Got no task")
    if not isinstance(task, Task):
        raise ValueError("task was not a Task object")
    batchjobs = BatchJobs(jobs=[])
    while True:
        # Check if we have any subjects left in the list
        if len(subjects_not_picked_yet) > 0:
            console.print(f"Picking a random main subject")
            qid = random.choice(subjects_not_picked_yet)
            subjects_not_picked_yet.remove(qid)
            job = process_qid_into_job(
                qid=qid,
                task=task,
                args=args,
                confirmation=args.no_confirmation,
            )
            if job is not None:
                # We first check if the job can be approved automatically
                if (
                    config.automatically_approve_jobs_with_less_than_fifty_matches
                    and len(job.items.number_of_items) < 50
                ):
                    console.print(
                        f"This job with {job.items.number_of_items} matching items was automatically approved",
                        style="green",
                    )
                    batchjobs.jobs.append(job)
                else:
                    # Here we check if the user has enabled no ask more limit.
                    if args.no_ask_match_more_limit is None:
                        logger.debug("No ask more was None")
                        job.items.print_items_list(args=args)
                        job.suggestion.print_search_strings()
                        answer = ask_add_to_job_queue(job)
                        if answer:
                            batchjobs.jobs.append(job)
                    else:
                        batchjobs.jobs.append(job)
                logger.debug(f"joblist now has {len(batchjobs.jobs)} jobs")
            print_job_statistics(batchjobs=batchjobs)
            if len(subjects_not_picked_yet) > 0:
                if (
                    args.no_ask_match_more_limit is None
                    or args.no_ask_match_more_limit
                    < sum(
                        len(job.items.list)
                        for job in batchjobs.jobs
                        if job.items.list is not None
                    )
                ):
                    answer_was_yes = ask_yes_no_question("Match one more?")
                    if not answer_was_yes:
                        break
            else:
                console.print("No more subjects in the list.")
                break
        else:
            console.print("No more subjects in the list. Exiting.")
            break
    if args.no_ask_match_more_limit is not None:
        batchjobs_limit = BatchJobs(jobs=[])
        for job in batchjobs.jobs:
            job.items.print_items_list(args=args)
            job.suggestion.print_search_strings()
            answer = ask_add_to_job_queue(job)
            if answer:
                batchjobs_limit.jobs.append(job)
        return batchjobs_limit
    return batchjobs
