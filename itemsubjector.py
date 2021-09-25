import argparse
import logging
import os
import random
from datetime import datetime
from typing import List, Union

from wikibaseintegrator import wbi_login, wbi_config

import config
from helpers.console import console, print_found_items_table, ask_add_to_job_queue, print_running_jobs, \
    ask_yes_no_question, print_finished, \
    print_keep_an_eye_on_wdqs_lag, print_best_practice
from helpers.enums import TaskIds
from helpers.menus import select_task
from helpers.migration import migrate_pickle_detection
from helpers.pickle import parse_pickle, remove_pickle, add_to_pickle, check_if_pickle_exists
from models.batch_job import BatchJob
from models.riksdagen_documents import RiksdagenDocumentItems
from models.scholarly_articles import ScholarlyArticleItems
from models.suggestion import Suggestion
from models.task import Task
from models.wikidata import Item
from tasks import tasks

logging.basicConfig(level=logging.WARNING)

# pseudo code
# let user choose what to work on
# e.g. Swedish documents from Riksdagen
# e.g. English scientific articles


def process_qid_into_job(qid: str = None,
                         task: Task = None,
                         args: argparse.Namespace = None) -> Union[BatchJob, None]:
    logger = logging.getLogger(__name__)
    if qid is None:
        raise ValueError("qid was None")
    if args is None:
        raise ValueError("args was None")
    if task is None:
        raise ValueError("task was None")
    if "https://www.wikidata.org/wiki/" in qid:
        qid = qid[30:]
    if "http://www.wikidata.org/entity/" in qid:
        qid = qid[31:]
    logger.debug(f"qid:{qid}")
    item = Item(
        id=qid,
        task=task
    )
    if "protein " in item.label.lower() and args.match_existing_main_subjects:
        console.print("Skipping protein which is too hard to validate "
                      "given the information in the label and description")
        return None
    else:
        console.print(f"Working on {item}")
        # generate suggestion with all we need
        suggestion = Suggestion(
            item=item,
            task=task,
            args=args
        )
        with console.status(f'Fetching items with labels that have one of '
                            f'the search strings by running a total of '
                            f'{len(suggestion.search_strings)} queries on WDQS...'):
            # TODO move this into task.py
            if task.id == TaskIds.SCHOLARLY_ARTICLES:
                items = ScholarlyArticleItems()
            elif task.id == TaskIds.RIKSDAGEN_DOCUMENTS:
                items = RiksdagenDocumentItems()
            else:
                raise ValueError(f"{task.id} was not recognized")
            items.fetch_based_on_label(suggestion=suggestion,
                                       task=task)
        if len(items.list) > 0:
            # Randomize the list
            items.random_shuffle_list()
            print_found_items_table(args=args,
                                    items=items)
            job = BatchJob(
                items=items,
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
    for qid in args.list:
        jobs.append(process_qid_into_job(qid=qid,
                                         task=task,
                                         args=args))
    return jobs


def login():
    with console.status("Logging in with WikibaseIntegrator..."):
        config.login_instance = wbi_login.Login(
            auth_method='login',
            user=config.username,
            password=config.password,
            debug=False
        )
        # Set User-Agent
        wbi_config.config["USER_AGENT_DEFAULT"] = config.user_agent


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
        job.run(jobs=jobs, job_count=count)
    print_finished()
    end_time = datetime.now()
    console.print(f'Total runtime: {end_time - start_time}')


def handle_existing_pickle():
    if check_if_pickle_exists():
        answer = ask_yes_no_question("A prepared list of jobs already exist, "
                                     "do you want to overwrite it? "
                                     "(pressing no will append to it)")
        if answer:
            remove_pickle()


def handle_preparation_or_run_directly(args: argparse.Namespace = None,
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
                              f"{sum(len(job.items.list) for job in jobs)} items")
                console.print(f"You can run the jobs "
                              f"non-interactively e.g. on the Toolforge "
                              f"Kubernetes cluster using -r or --run-prepared-jobs. "
                              f"See https://phabricator.wikimedia.org/T285944 "
                              f"for details")
            else:
                raise ValueError("Pickle file had no jobs")
    else:
        run_jobs(jobs)


def setup_argparse_and_return_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list',
                        nargs='+',
                        help=('List of QIDs or URLs to Q-items that '
                              'are to be added as '
                              'main subjects on scientific articles. '
                              'Always add the most specific ones first. '
                              'See the README for examples'),
                        required=False)
    parser.add_argument('-na', '--no-aliases',
                        action='store_true',
                        help='Turn off alias matching'
                        )
    parser.add_argument('-p', '--prepare-jobs',
                        action='store_true',
                        help='Prepare a job for later execution, e.g. in a job engine'
                        )
    parser.add_argument('-r', '--run-prepared-jobs',
                        action='store_true',
                        help='Run prepared jobs non-interactively'
                        )
    parser.add_argument('-rm', '--remove-prepared-jobs',
                        action='store_true',
                        help='Remove prepared jobs'
                        )
    parser.add_argument('-m', '--match-existing-main-subjects',
                        action='store_true',
                        help=('Match from list of 136.000 already used '
                              'main subjects on other scientific articles')
                        )
    parser.add_argument('-w', '--limit-to-items-without-p921',
                        action='store_true',
                        help='Limit matching to scientific articles without P921 main subject'
                        )
    parser.add_argument('-su', '--show-search-urls',
                        action='store_true',
                        help='Show an extra column in the table of search strings with links'
                        )
    parser.add_argument('-iu', '--show-item-urls',
                        action='store_true',
                        help='Show an extra column in the table of items with links'
                        )
    return parser.parse_args()


def get_main_subjects_from_file() -> List[str]:
    # read the data file
    file_path = "data/main_subjects.csv"
    main_subjects_path = f"{os.getcwd()}/{file_path}"
    with open(main_subjects_path) as file:
        lines = file.readlines()
        main_subjects = [line.rstrip() for line in lines]
    return main_subjects


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
    main_subjects = get_main_subjects_from_file()
    handle_existing_pickle()
    console.print(f"The list included with the tool currently "
                  f"have {len(main_subjects)} main subjects that "
                  f"appeared on scholarly articles at least once "
                  f"2021-09-24 when it was generated.")
    jobs = get_validated_random_subjects(args=args, main_subjects=main_subjects)
    handle_preparation_or_run_directly(args=args, jobs=jobs)


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
    if args.match_existing_main_subjects is True:
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
        handle_existing_pickle()
        task: Task = select_task()
        if task is None:
            raise ValueError("Got no task")
        jobs = process_user_supplied_qids_into_batch_jobs(args=args, task=task)
        handle_preparation_or_run_directly(args=args, jobs=jobs)


if __name__ == "__main__":
    main()
