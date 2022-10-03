# from __future__ import annotations

import argparse
import logging
import random
from time import sleep
from typing import List, Optional

from pydantic import BaseModel
from wikibaseintegrator.wbi_helpers import execute_sparql_query  # type: ignore

import config
from src.helpers.cli_messages import print_job_statistics
from src.helpers.console import console
from src.helpers.menus import select_task
from src.helpers.questions import ask_add_to_job_queue, ask_yes_no_question
from src.models.batch_jobs import BatchJobs
from src.models.wikimedia.wikidata.item.main_subject import MainSubjectItem
from src.tasks import Task

logger = logging.getLogger(__name__)


class MainSubjects(BaseModel):
    args: argparse.Namespace
    task: Optional[Task] = None
    main_subjects: List[str] = []
    batchjobs: BatchJobs = BatchJobs(jobs=[])

    class Config:
        arbitrary_types_allowed = True

    def match_main_subjects_from_sparql(self):
        """Collect subjects via SPARQL and call get_validated_main_subjects()
        If we get any validated jobs we handle them"""
        if self.args is None or self.args.sparql is None:
            raise ValueError("args.sparql was None")
        self.__check_different_from__()
        self.__fetch_main_subjects__()
        if self.main_subjects:
            console.print(f"Got {len(self.main_subjects)} results")
            sleep(1)
            self.get_validated_main_subjects_as_jobs()
            self.handle_job_preparation_or_run_directly_if_any_jobs()
        else:
            console.print("Got 0 results. Try another query or debug it using --debug")

    # def process_user_supplied_qids_into_batch_jobs(self) -> List[BatchJob]:
    #     """Given a sparql_items of QIDs, we go through
    #     them and return a sparql_items of jobs"""
    #     # TODO this should not return anything
    #     if self.task:
    #         print_best_practice(self.task)
    #         jobs = []
    #         for qid in self.args.add:
    #             main_subject_item = MainSubjectItem(id=qid, args=self.args, task=self.task)
    #             job = main_subject_item.fetch_items_and_get_job_if_confirmed()
    #             if job:
    #                 jobs.append(job)
    #         return jobs
    #     return []

    def handle_job_preparation_or_run_directly_if_any_jobs(self):
        if self.batchjobs is None:
            raise ValueError("batchjobs was None")
        if self.args is None:
            raise ValueError("args was None")
        if self.batchjobs.number_of_jobs:
            if self.args.prepare_jobs:
                console.print(
                    f"Adding {self.batchjobs.number_of_jobs} job(s) "
                    f"to the jobs file"
                )
                for job in self.batchjobs.jobs:
                    from src import add_to_job_pickle

                    add_to_job_pickle(job)
                print_job_statistics(batchjobs=self.batchjobs)
                console.print(
                    f"You can run the jobs "
                    f"non-interactively e.g. on the Toolforge "
                    f"Kubernetes cluster using -r or --run-prepared-jobs. "
                    f"See Kubernetes_HOWTO.md for details."
                )
            else:
                self.batchjobs.run_jobs()

    def get_validated_main_subjects_as_jobs(
        self,
    ) -> None:
        """This function randomly picks a subject and add it to the
        sparql_items of jobs if it had any matches and the user approved it"""
        # TODO break this down into smaller methods
        qid_subjects_not_picked_yet = self.main_subjects
        self.__select_task__()
        while True:
            # Check if we have any subjects left in the sparql_items
            if len(qid_subjects_not_picked_yet):
                console.print(f"Picking a random main subject")
                qid = random.choice(qid_subjects_not_picked_yet)
                qid_subjects_not_picked_yet.remove(qid)
                main_subject_item = MainSubjectItem(
                    id=qid,
                    args=self.args,
                    task=self.task,
                    confirmation=self.args.no_confirmation,
                )
                job = main_subject_item.fetch_items_and_get_job_if_confirmed()
                if job:
                    # Here we check if the user has enabled no ask more limit.
                    if self.args.no_ask_match_more_limit is None:
                        logger.debug("No ask more was None")
                        if job.main_subject_item.items:
                            job.main_subject_item.items.print_items_list(args=self.args)
                            job.main_subject_item.print_search_strings()
                            answer = ask_add_to_job_queue(job)
                            if answer:
                                self.batchjobs.jobs.append(job)
                    else:
                        self.batchjobs.jobs.append(job)
                logger.debug(f"joblist now has {self.batchjobs.number_of_jobs} jobs")
                print_job_statistics(batchjobs=self.batchjobs)
                if len(qid_subjects_not_picked_yet):
                    if (
                        self.args.no_ask_match_more_limit is None
                        or self.args.no_ask_match_more_limit
                        < sum(
                            job.main_subject_item.items.number_of_sparql_items
                            for job in self.batchjobs.jobs
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
        if self.args.no_ask_match_more_limit:
            for job in self.batchjobs.jobs:
                if job.main_subject_item.items:
                    job.main_subject_item.items.print_items_list(args=self.args)
                    job.main_subject_item.print_search_strings()
                    if (
                        config.automatically_approve_jobs_with_less_than_fifty_matches
                        and job.main_subject_item.items.number_of_sparql_items < 50
                    ):
                        console.print(
                            f"This job with {job.main_subject_item.items.number_of_sparql_items} matching items was automatically approved",
                            style="green",
                        )
                        self.batchjobs.jobs.append(job)
                    else:
                        answer = ask_add_to_job_queue(job)
                        if answer:
                            self.batchjobs.jobs.append(job)

    def __select_task__(self):
        self.task: Task = select_task()
        if self.task is None:
            raise ValueError("Got no task")

    def __fetch_main_subjects__(self):
        with console.status("Running query on WDQS..."):
            results = execute_sparql_query(
                self.args.sparql.replace("{", "{{").replace("}", "}}"),
            )
            for item_json in results["results"]["bindings"]:
                logging.debug(f"item_json:{item_json}")
                self.main_subjects.append(item_json["item"]["value"])

    def __check_different_from__(self):
        if "P1889" not in self.args.sparql:
            console.print(
                "Your SPARQL did not contain P1889 (different from). "
                "Please include 'MINUS {?main_subject_item wdt:P1889 [].}' "
                "in your WHERE clause to avoid false positives."
            )
            exit(0)
        else:
            logger.info("Detected P1889 in the query")


