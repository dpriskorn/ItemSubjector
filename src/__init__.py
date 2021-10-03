import argparse
import logging
import random
from datetime import datetime
from typing import List, Union

from wikibaseintegrator import wbi_login, wbi_config
from wikibaseintegrator.wbi_helpers import execute_sparql_query

import config
from src.helpers.argparse_setup import setup_argparse_and_return_args
from src.helpers.cleaning import strip_prefix
from src.helpers.console import console, print_found_items_table, ask_add_to_job_queue, print_running_jobs, \
    ask_yes_no_question, print_finished, \
    print_keep_an_eye_on_wdqs_lag, print_best_practice, print_job_statistics, ask_discard_existing_job_pickle
from src.helpers.enums import TaskIds
from src.helpers.menus import select_task
from src.helpers.migration import migrate_pickle_detection
from src.helpers.pickle import parse_job_pickle, remove_pickle, add_to_job_pickle, check_if_pickle_exists, \
    parse_main_subjects_pickle
from src.models.batch_job import BatchJob
from src.models.riksdagen_documents import RiksdagenDocumentItems
from src.models.scholarly_articles import ScholarlyArticleItems
from src.models.suggestion import Suggestion
from src.models.task import Task
from src.models.thesis import ThesisItems
from src.models.wikidata import Item
from src.tasks import tasks

logging.basicConfig(level=logging.WARNING)


# pseudo code
# let user choose what to work on
# e.g. Swedish documents from Riksdagen
# e.g. English scientific articles


def process_qid_into_job(qid: str = None,
                         task: Task = None,
                         args: argparse.Namespace = None,
                         confirmation: bool = False) -> Union[BatchJob, None]:
    # logger = logging.getLogger(__name__)
    if qid is None:
        raise ValueError("qid was None")
    if args is None:
        raise ValueError("args was None")
    if task is None:
        raise ValueError("task was None")
    item = Item(
        id=strip_prefix(qid),
        task=task
    )
    if item.label is not None:
        console.print(f"Working on {item}")
        # generate suggestion with all we need
        suggestion = Suggestion(
            item=item,
            task=task,
            args=args
        )
        if confirmation:
            answer = ask_yes_no_question("Do you want to continue?")
            if not answer:
                return None
        with console.status(f'Fetching items with labels that have one of '
                            f'the search strings by running a total of '
                            f'{len(suggestion.search_strings) * task.number_of_queries_per_search_string} '
                            f'queries on WDQS...'):
            if task.id == TaskIds.SCHOLARLY_ARTICLES:
                items = ScholarlyArticleItems()
            elif task.id == TaskIds.RIKSDAGEN_DOCUMENTS:
                items = RiksdagenDocumentItems()
            elif task.id == TaskIds.THESIS:
                items = ThesisItems()
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
            return None
    else:
        console.print(f"Label for {task.language_code} was None on {item.url()}, skipping")

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


def run_jobs(jobs: List[BatchJob] = None):
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


def handle_job_preparation_or_run_directly_if_any_jobs(args: argparse.Namespace = None,
                                                       jobs: List[BatchJob] = None):
    if len(jobs) > 0:
        if args.prepare_jobs:
            console.print(f"Adding {len(jobs)} job(s) to the jobs file")
            for job in jobs:
                add_to_job_pickle(job)
            print_job_statistics(jobs=jobs)
            console.print(f"You can run the jobs "
                          f"non-interactively e.g. on the Toolforge "
                          f"Kubernetes cluster using -r or --run-prepared-jobs. "
                          f"See https://phabricator.wikimedia.org/T285944 "
                          f"for details")
        else:
            run_jobs(jobs)


def get_validated_main_subjects(args: argparse.Namespace = None,
                                main_subjects: List[str] = None,
                                jobs: List[BatchJob] = None):
    """This function randomly picks a subject and present it for validation"""
    # logger = logging.getLogger(__name__)
    if jobs is None:
        raise ValueError("jobs was None")
    if not isinstance(jobs, List):
        raise ValueError("jobs was not a list")
    if args is None:
        raise ValueError("args was None")
    if main_subjects is None:
        raise ValueError("main subjects was None")
    # TODO implement better check for duplicates to avoid wasting resources
    picked_before = []
    while True:
        console.print(f"Picking a random main subject")
        qid = random.choice(main_subjects)
        if qid not in picked_before:
            job = process_qid_into_job(qid=qid,
                                       # The scientific article task is hardcoded for now
                                       task=tasks[0],
                                       args=args,
                                       confirmation=True)
            if job is not None:
                jobs.append(job)
                picked_before.append(qid)
            print_job_statistics(jobs=jobs)
            answer = ask_yes_no_question("Match one more?")
            if not answer:
                break
        else:
            console.print("Skipping already picked qid")
    return jobs


def match_existing_main_subjects(args: argparse.Namespace = None,
                                 jobs: List[BatchJob] = None):
    if jobs is None:
        raise ValueError("jobs was None")
    if not isinstance(jobs, List):
        raise ValueError("jobs was not a list")
    with console.status("Reading the main subjects file into memory"):
        main_subjects = parse_main_subjects_pickle()
    # raise Exception("debug exit")
    jobs = get_validated_main_subjects(args=args,
                                       main_subjects=main_subjects,
                                       jobs=jobs)
    handle_job_preparation_or_run_directly_if_any_jobs(args=args, jobs=jobs)


def match_main_subjects_from_sparql(args: argparse.Namespace = None,
                                    jobs: List[BatchJob] = None):
    """Collect subjects via SPARQL and call get_validated_main_subjects()
    If we get any validated jobs we handle them"""
    if jobs is None:
        raise ValueError("jobs was None")
    if not isinstance(jobs, List):
        raise ValueError("jobs was not a list")
    with console.status("Running query on WDQS..."):
        main_subjects = []
        results = execute_sparql_query(args.sparql.replace("{", "{{").replace("}", "}}"),
                                       debug=args.debug_sparql)
        for item_json in results["results"]["bindings"]:
            logging.debug(f"item_json:{item_json}")
            main_subjects.append(item_json["item"]["value"])
    if len(main_subjects) > 0:
        console.print(f"Got {len(main_subjects)} results")
        jobs = get_validated_main_subjects(
            args=args,
            main_subjects=main_subjects,
            jobs=jobs
        )
        handle_job_preparation_or_run_directly_if_any_jobs(args=args, jobs=jobs)
    else:
        console.print("Got 0 results. Try another query or debug it using --debug")


def main():
    """This is the main function that makes everything else happen"""
    # logger = logging.getLogger(__name__)
    migrate_pickle_detection()
    jobs: List[BatchJob] = []
    args = setup_argparse_and_return_args()
    # console.print(args.list)
    if args.run_prepared_jobs is True:
        jobs = parse_job_pickle()
        if jobs is not None and len(jobs) > 0:
            run_jobs(jobs)
            # Remove the pickle afterwards
            remove_pickle()
    if args.remove_prepared_jobs is True:
        remove_pickle()
        console.print("Removed the job list.")
        # exit(0)
    if args.prepare_jobs is True:
        if check_if_pickle_exists(config.job_pickle_file_path):
            if not ask_discard_existing_job_pickle():
                # We run this if the user answered no to discarding which
                # is the default to avoid running batches multiple times by
                # mistake (which does not harm Wikidata, but waste computing
                # resources which is bad.
                jobs = parse_job_pickle(silent=True)
                if len(jobs) > 0:
                    console.print(f"Found and loaded {len(jobs)} "
                                  f"jobs with a total of "
                                  f"{sum(len(job.items.list) for job in jobs)} items")
            remove_pickle(silent=True)
    if args.match_existing_main_subjects is True:
        match_existing_main_subjects(args=args, jobs=jobs)
    elif args.sparql:
        match_main_subjects_from_sparql(args=args, jobs=jobs)
    else:
        if args.add is None:
            console.print("Got no QIDs. Quitting")
            exit(0)
        task: Task = select_task()
        if task is None:
            raise ValueError("Got no task")
        jobs.extend(process_user_supplied_qids_into_batch_jobs(args=args, task=task))
        handle_job_preparation_or_run_directly_if_any_jobs(args=args, jobs=jobs)


if __name__ == "__main__":
    main()
