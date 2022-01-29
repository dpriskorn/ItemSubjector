import argparse
import logging
from typing import List

import pandas as pd
from wikibaseintegrator import wbi_login, wbi_config
from wikibaseintegrator.wbi_helpers import execute_sparql_query

import config
from src.helpers.argparse_setup import setup_argparse_and_return_args
from src.helpers.cleaning import strip_prefix
from src.helpers.console import console, print_found_items_table, ask_add_to_job_queue, print_running_jobs, \
    ask_yes_no_question, print_finished, \
    print_keep_an_eye_on_wdqs_lag, print_best_practice, print_job_statistics, ask_discard_existing_job_pickle
from src.helpers.enums import TaskIds
from src.helpers.jobs import process_qid_into_job, process_user_supplied_qids_into_batch_jobs, run_jobs, \
    handle_job_preparation_or_run_directly_if_any_jobs, get_validated_main_subjects_as_jobs
from src.helpers.menus import select_task
from src.helpers.migration import migrate_pickle_detection
from src.helpers.pickle import parse_job_pickle, remove_job_pickle, add_to_job_pickle, check_if_pickle_exists, \
    parse_main_subjects_pickle, get_hash_of_job_pickle
from src.models.batch_job import BatchJob
from src.models.quickstatements import QuickStatementsCommandVersion1
from src.models.suggestion import Suggestion
from src.models.task import Task
from src.models.wikidata import Item, EntityID
from src.tasks import tasks


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


def match_existing_main_subjects(args: argparse.Namespace = None,
                                 jobs: List[BatchJob] = None):
    if jobs is None:
        raise ValueError("jobs was None")
    if not isinstance(jobs, List):
        raise ValueError("jobs was not a list")
    with console.status("Reading the main subjects file into memory"):
        main_subjects = parse_main_subjects_pickle()
    # raise Exception("debug exit")
    jobs = get_validated_main_subjects_as_jobs(args=args,
                                               main_subjects=main_subjects,
                                               jobs=jobs)
    handle_job_preparation_or_run_directly_if_any_jobs(args=args, jobs=jobs)


def match_main_subjects_from_sparql(args: argparse.Namespace = None,
                                    jobs: List[BatchJob] = None):
    """Collect subjects via SPARQL and call get_validated_main_subjects()
    If we get any validated jobs we handle them"""
    logger = logging.getLogger(__name__)
    if jobs is None:
        raise ValueError("jobs was None")
    if not isinstance(jobs, List):
        raise ValueError("jobs was not a list")
    if "P1889" not in args.sparql:
        console.print("Your SPARQL did not contain P1889 (different from). "
                      "Please include 'MINUS {?item wdt:P1889 [].}' "
                      "in your WHERE clause to avoid false positives.")
        exit(0)
    else:
        logger.info("Detected P1889 in the query")
    with console.status("Running query on WDQS..."):
        main_subjects = []
        results = execute_sparql_query(args.sparql.replace("{", "{{").replace("}", "}}"),
                                       debug=args.debug_sparql)
        for item_json in results["results"]["bindings"]:
            logging.debug(f"item_json:{item_json}")
            main_subjects.append(item_json["item"]["value"])
    if len(main_subjects) > 0:
        console.print(f"Got {len(main_subjects)} results")
        jobs = get_validated_main_subjects_as_jobs(
            args=args,
            main_subjects=main_subjects,
            jobs=jobs
        )
        handle_job_preparation_or_run_directly_if_any_jobs(args=args, jobs=jobs)
    else:
        console.print("Got 0 results. Try another query or debug it using --debug")


def export_jobs_to_dataframe():
    logger = logging.getLogger(__name__)
    logger.info("Exporting jobs to DataFrame. All jobs are appended to one frame")
    jobs = parse_job_pickle()
    number_of_jobs = len(jobs)
    if jobs is not None and number_of_jobs > 0:
        logger.info(f"Found {number_of_jobs} jobs")
        df = pd.DataFrame()
        count = 1
        for job in jobs:
            count += 1
            logger.info(f"Working on job {count}/{number_of_jobs}")
            job_df = pd.DataFrame()
            for item in job.items.list:
                job_df = job_df.append(pd.DataFrame(data=[dict(
                    qid=item.id,
                    label=item.label,
                    description=item.description
                )]))
            df = df.append(job_df)
            logger.debug(f"Added {len(job.items.list)} items to the dataframe")
        logger.debug(f"Exporting {len(df)} rows to pickle")
        pickle_filename = "dataframe.pkl.gz"
        df.to_pickle(pickle_filename)
        console.print(f"Wrote to {pickle_filename} in the current directory")


def export_jobs_to_quickstatements():
    logger = logging.getLogger(__name__)
    logger.info("Exporting jobs to QuickStatements V1 commands. One file for each job.")
    jobs = parse_job_pickle()
    if jobs is not None and len(jobs) > 0:
        for job in jobs:
            # Convert all items
            lines = []
            for item in job.items.list:
                line = QuickStatementsCommandVersion1(
                    target=EntityID(item.id),
                    property=EntityID("P921"),
                    value=EntityID(job.suggestion.item.id),
                )
                lines.append(line)
            logger.debug(f"Got {len(lines)} QS lines to export")
            filename = (f"quickstatements-export-"
                        f"{job.suggestion.item.id}-"
                        f"{job.suggestion.item.label}.csv")
            with open(filename, "w") as file:
                for line in lines:
                    file.write(f"{str(line)}\n")
            console.print(f"Wrote to {filename} in the current directory")


def main():
    """This is the main function that makes everything else happen"""
    logger = logging.getLogger(__name__)
    migrate_pickle_detection()
    jobs: List[BatchJob] = []
    args = setup_argparse_and_return_args()
    # console.print(args.list)
    if args.remove_prepared_jobs is True:
        remove_job_pickle()
        console.print("Removed the job list.")
        # exit(0)
    if args.prepare_jobs is True:
        logger.info("Preparing jobs")
        if check_if_pickle_exists(config.job_pickle_file_path):
            if not ask_discard_existing_job_pickle():
                # the default is yes
                # to avoid running batches multiple times by
                # mistake (which does not harm Wikidata, but waste
                # precious computing resources which we want to avoid.)
                jobs = parse_job_pickle(silent=True)
                if len(jobs) > 0:
                    console.print(f"Found and loaded {len(jobs)} "
                                  f"jobs with a total of "
                                  f"{sum(len(job.items.list) for job in jobs)} items")
            remove_job_pickle(silent=True)
    if args.run_prepared_jobs is True:
        logger.info("Running prepared jobs")
        jobs = parse_job_pickle()
        if jobs is not None and len(jobs) > 0:
            file_hash = get_hash_of_job_pickle()
            run_jobs(jobs)
            # Remove the pickle afterwards
            remove_job_pickle(hash=file_hash)
    if args.export_job_list_to_quickstatements:
        export_jobs_to_quickstatements()
    elif args.export_jobs_to_dataframe:
        export_jobs_to_dataframe()
    elif args.match_existing_main_subjects is True:
        match_existing_main_subjects(args=args, jobs=jobs)
    elif args.sparql:
        match_main_subjects_from_sparql(args=args, jobs=jobs)
    else:
        # if not args.run_prepared_jobs:
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
