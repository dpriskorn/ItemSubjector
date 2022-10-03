import argparse
import logging

import pandas as pd  # type: ignore
from pydantic import BaseModel
from wikibaseintegrator import wbi_config, wbi_login  # type: ignore
from wikibaseintegrator.wbi_helpers import execute_sparql_query  # type: ignore

import config
from src.helpers.argparse_setup import setup_argparse_and_return_args
from src.helpers.cli_messages import (
    print_best_practice,
    print_finished,
    print_found_items_table,
    print_job_statistics,
)
from src.helpers.console import console, print_keep_an_eye_on_wdqs_lag
from src.helpers.enums import TaskIds
from src.helpers.jobs import (
    get_validated_main_subjects_as_jobs,
    handle_job_preparation_or_run_directly_if_any_jobs,
    process_user_supplied_qids_into_batch_jobs,
)
from src.helpers.menus import select_task
from src.helpers.migration import migrate_pickle_detection
from src.helpers.pickle import (
    add_to_job_pickle,
    check_if_pickle_exists,
    get_hash_of_job_pickle,
    parse_job_pickle,
    remove_job_pickle,
)
from src.helpers.questions import (
    ask_add_to_job_queue,
    ask_discard_existing_job_pickle,
    ask_yes_no_question,
)
from src.models.batch_job import BatchJob
from src.models.batch_jobs import BatchJobs
from src.models.suggestion import Suggestion
from src.models.task import Task
from src.models.wikimedia.wikidata.entiyt_id import EntityId
from src.tasks import tasks

logging.basicConfig(level=config.loglevel)


class ItemSubjector(BaseModel):
    @staticmethod
    def match_main_subjects_from_sparql(args: argparse.Namespace = None):
        """Collect subjects via SPARQL and call get_validated_main_subjects()
        If we get any validated jobs we handle them"""
        logger = logging.getLogger(__name__)
        if args is None or args.sparql is None:
            raise ValueError("args.sparql was None")
        if "P1889" not in args.sparql:
            console.print(
                "Your SPARQL did not contain P1889 (different from). "
                "Please include 'MINUS {?main_subject_item wdt:P1889 [].}' "
                "in your WHERE clause to avoid false positives."
            )
            exit(0)
        else:
            logger.info("Detected P1889 in the query")
        with console.status("Running query on WDQS..."):
            main_subjects = []
            results = execute_sparql_query(
                args.sparql.replace("{", "{{").replace("}", "}}"),
            )
            for item_json in results["results"]["bindings"]:
                logging.debug(f"item_json:{item_json}")
                main_subjects.append(item_json["item"]["value"])
        if main_subjects:
            console.print(f"Got {len(main_subjects)} results")
            batchjobs = get_validated_main_subjects_as_jobs(
                args=args, main_subjects=main_subjects
            )
            handle_job_preparation_or_run_directly_if_any_jobs(
                args=args, batchjobs=batchjobs
            )
        else:
            console.print("Got 0 results. Try another query or debug it using --debug")

    @staticmethod
    def export_jobs_to_dataframe():
        logger = logging.getLogger(__name__)
        logger.info("Exporting jobs to DataFrame. All jobs are appended to one frame")
        batchjobs = parse_job_pickle()
        if batchjobs:
            if batchjobs and batchjobs.number_of_jobs > 0:
                logger.info(f"Found {batchjobs.number_of_jobs} jobs")
                df = pd.DataFrame()
                count = 1
                for job in batchjobs.jobs:
                    count += 1
                    logger.info(f"Working on job {count}/{batchjobs.number_of_jobs}")
                    job_df = pd.DataFrame()
                    for item in job.main_subject_item.items.sparql_items:
                        job_df = job_df.append(
                            pd.DataFrame(
                                data=[
                                    dict(
                                        qid=item.id,
                                        label=item.label,
                                        description=item.description,
                                    )
                                ]
                            )
                        )
                    df = df.append(job_df)
                    logger.debug(
                        f"Added {len(job.main_subject_item.items.sparql_items)} items to the dataframe"
                    )
                logger.debug(f"Exporting {len(df)} rows to pickle")
                pickle_filename = "dataframe.pkl.gz"
                df.to_pickle(pickle_filename)
                console.print(f"Wrote to {pickle_filename} in the current directory")
        else:
            console.print(
                "No jobs found. Create a job sparql_items first by using '--prepare-jobs'"
            )

    def run(self):
        """This is the main function that makes everything else happen"""
        logger = logging.getLogger(__name__)
        migrate_pickle_detection()
        args = setup_argparse_and_return_args()
        # console.print(args.sparql_items)
        if args.remove_prepared_jobs is True:
            remove_job_pickle()
            console.print("Removed the job sparql_items.")
            # exit(0)
        if args.prepare_jobs is True:
            logger.info("Preparing jobs")
            if check_if_pickle_exists(config.job_pickle_file_path):
                if ask_discard_existing_job_pickle():
                    remove_job_pickle(silent=True)
                else:
                    console.print("Quitting.")
        if args.run_prepared_jobs is True:
            logger.info("Running prepared jobs")
            batchjobs = parse_job_pickle()
            if batchjobs and len(batchjobs.jobs) > 0:
                file_hash = get_hash_of_job_pickle()
                batchjobs.run_jobs()
                # Remove the pickle afterwards
                remove_job_pickle(hash=file_hash)
        elif args.export_jobs_to_dataframe:
            self.export_jobs_to_dataframe()
        elif args.sparql:
            self.match_main_subjects_from_sparql(args=args)
        else:
            # if not args.run_prepared_jobs:
            if args.add is None:
                console.print("Got no arguments or QIDs. Try '--help' for help.")
                exit(0)
            batchjobs = get_validated_main_subjects_as_jobs(
                args=args, main_subjects=args.add
            )
            handle_job_preparation_or_run_directly_if_any_jobs(
                args=args, batchjobs=batchjobs
            )
