import argparse
import logging
import random
from typing import List

from helpers.argparse_setup import setup_argparse_and_return_args
from helpers.cleaning import strip_prefix
from helpers.console import console, print_found_items_table, ask_add_to_job_queue, ask_yes_no_question
from helpers.jobs import process_qid_into_job, process_user_supplied_qids_into_batch_jobs, run_jobs, \
    do_job_preparation_or_run_directly
from helpers.menus import select_task
from helpers.migration import migrate_pickle_detection
from helpers.pickle import parse_pickle, remove_pickle, handle_existing_pickle
from helpers.read_data import get_main_subjects_from_file
from models.batch_job import BatchJob
from models.deletion_target import DeletionTarget
from models.task import Task
from models.wikidata import Item
from tasks import tasks

logging.basicConfig(level=logging.WARNING)

# pseudo code
# let user choose what to work on
# e.g. Swedish documents from Riksdagen
# e.g. English scientific articles
# branch off based on command line arguments


def delete_qid_from_items(args: argparse.Namespace = None):
    """This function handles deleting a QID from P921
    on items with any of the QIDs specified in --from on P921

    We only allow deleting one QID at a time"""
    if args is None:
        raise ValueError("args was None")
    # Check if the target QID appear in from
    from_qids = []
    for qid in args.from_items_with:
        from_qids.append(strip_prefix(qid))
    target_qid = strip_prefix(args.delete)
    if target_qid in from_qids:
        console.print("Error. The QID to delete "
                      "cannot be in the from items also. "
                      "See the README or run 'itemsubjector.py -h'")
        exit(0)
    # let user choose a task
    task: Task = select_task()
    if task is None:
        raise ValueError("Got no task")
    # convert list of QIDs into List[Item]
    from_main_subjects = []
    for qid in from_qids:
        from_main_subjects.append(Item(
            id=qid,
            task=task
        ))
    # convert the target qid
    target = DeletionTarget(
        item=Item(
            id=target_qid,
            task=task
        )
    )
    # get the from items
    console.print(f"Working on deleting {target.item.label} from items")
    with console.status(f'Fetching items by running a total of '
                        f'{len(from_main_subjects)} queries on WDQS...'):
        task.items.fetch_based_on_main_subject(main_subjects=from_main_subjects,
                                               target=target)
    # present what is gonna happen in a table
    if len(task.items.list) > 0:
        # Randomize the list
        task.items.random_shuffle_list()
        print_found_items_table(args=args,
                                task=task)
        job = BatchJob(
                target=target,
                task=task
        )
        # ask the user to validate
        answer = ask_add_to_job_queue(job)
        if answer:
            # convert into BatchJob
            jobs = [job]
            # handle pickle
            if args.prepare_jobs:
                handle_existing_pickle()
            # handle running
            do_job_preparation_or_run_directly(args=args, jobs=jobs)
    else:
        console.print("No matching items found")


def get_validated_random_subjects(args: argparse.Namespace = None,
                                  main_subjects: List[str] = None):
    if args is None:
        raise ValueError("args was None")
    if main_subjects is None:
        raise ValueError("main subjects was None")
    picked_before = []
    jobs = []
    while True:
        console.print(f"Picking a random main subject")
        qid = random.choice(main_subjects)
        if qid not in picked_before:
            job = process_qid_into_job(qid=qid,
                                       # The scientific article task is hardcoded for now
                                       task=tasks[0],
                                       args=args)
            if job is not None:
                jobs.append(job)
                picked_before.append(qid)
            answer = ask_yes_no_question("Match one more?")
            if not answer:
                break
        else:
            console.print("Skipping already picked qid")
    return jobs


def match_existing_main_subjects(args: argparse.Namespace = None):
    if args is None:
        raise ValueError("args was None")
    main_subjects = get_main_subjects_from_file()
    handle_existing_pickle()
    console.print(f"The list included with the tool currently "
                  f"have {len(main_subjects)} main subjects that "
                  f"appeared on scholarly articles at least once "
                  f"2021-09-24 when it was generated.")
    jobs = get_validated_random_subjects(args=args, main_subjects=main_subjects)
    do_job_preparation_or_run_directly(args=args, jobs=jobs)


def main():
    """This is the main function that makes everything else happen"""
    # logger = logging.getLogger(__name__)
    migrate_pickle_detection()
    args = setup_argparse_and_return_args()
    # console.print(args.list)
    if args.remove_prepared_jobs is True:
        remove_pickle()
        console.print("Removed the job list.")
        # exit(0)
    elif args.delete is not None:
        if args.from_items_with is not None and args.delete is not None:
            delete_qid_from_items(args=args)
        else:
            console.print("Error. Need both a QID to delete "
                          "and from which items to delete it. "
                          "See the README or run 'itemsubjector.py -h'")
            exit(0)
    elif args.match_existing_main_subjects is True:
        match_existing_main_subjects(args=args)
    elif args.run_prepared_jobs is True:
        # read pickle as list of BatchJobs
        jobs = parse_pickle()
        if jobs is not None and len(jobs) > 0:
            run_jobs(jobs)
            # Remove the pickle afterwards
            remove_pickle()
    else:
        if args.list is None:
            console.print("Got no QIDs. Quitting")
            exit(0)
        if args.prepare_jobs:
            handle_existing_pickle()
        task: Task = select_task()
        if task is None:
            raise ValueError("Got no task")
        jobs = process_user_supplied_qids_into_batch_jobs(args=args, task=task)
        do_job_preparation_or_run_directly(args=args, jobs=jobs)


if __name__ == "__main__":
    main()
