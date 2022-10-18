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
from src.models.main_subjects import MainSubjects
from src.models.task import Task
from src.models.wikimedia.wikidata.entiyt_id import EntityId
from src.tasks import tasks

logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__name__)


class ItemSubjector(BaseModel):
    @staticmethod
    def run():
        """This is the main function that makes everything else happen"""
        migrate_pickle_detection()
        args = setup_argparse_and_return_args()
        # console.print(args.sparql_items)
        if args.remove_prepared_jobs is True:
            remove_job_pickle()
            console.print("Removed the job sparql_items.")
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
        elif args.sparql:
            main_subjects = MainSubjects(args=args)
            main_subjects.match_main_subjects_from_sparql()
            main_subjects.get_validated_main_subjects_as_jobs()
            main_subjects.handle_job_preparation_or_run_directly_if_any_jobs()
        else:
            if args.add is None:
                console.print("Got no arguments or QIDs. Try '--help' for help.")
            else:
                main_subjects = MainSubjects(args=args, main_subjects=args.add)
                main_subjects.get_validated_main_subjects_as_jobs()
                main_subjects.handle_job_preparation_or_run_directly_if_any_jobs()
