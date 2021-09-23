import argparse
import logging

from wikibaseintegrator import wbi_login, wbi_config

import config
from helpers.console import console, print_scholarly_articles_best_practice_information, \
    print_riksdagen_documents_best_practice_information, \
    print_found_items_table, ask_continue_with_the_rest, print_running_jobs
from helpers.enums import TaskIds
from helpers.menus import select_task
from helpers.migration import migrate_pickle_detection
from helpers.pickle import parse_pickle, remove_pickle, add_to_pickle
from models.batch_job import BatchJob
from models.riksdagen_documents import RiksdagenDocumentItems
from models.scholarly_articles import ScholarlyArticleItems
from models.suggestion import Suggestion
from models.task import Task
from models.wikidata import Item

logging.basicConfig(level=logging.WARNING)

# pseudo code
# let user choose what to work on
# e.g. Swedish documents from Riksdagen
# e.g. English scientific articles


def process_user_supplied_qids_into_batch_jobs(args: argparse.Namespace = None,
                                               task: Task = None):
    """Given a list of QIDs, we go through
    them and call add_suggestion_to_items() on each one"""
    logger = logging.getLogger(__name__)
    if args is None:
        raise ValueError("args was None")
    if task is None:
        raise ValueError("task was None")
    if task.id == TaskIds.SCHOLARLY_ARTICLES:
        print_scholarly_articles_best_practice_information()
    elif task.id == TaskIds.RIKSDAGEN_DOCUMENTS:
        print_riksdagen_documents_best_practice_information()
    else:
        raise ValueError(f"taskid {task.id} not recognized")
    # login()
    jobs = []
    for qid in args.list:
        if "https://www.wikidata.org/wiki/" in qid:
            qid = qid[30:]
        if "http://www.wikidata.org/entity/" in qid:
            qid = qid[31:]
        logger.debug(f"qid:{qid}")
        item = Item(
            id=qid,
            task=task
        )
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
            print_found_items_table(items=items)
            ask_continue_with_the_rest()
            job = BatchJob(
                items=items,
                suggestion=suggestion
            )
            jobs.append(job)
        else:
            console.print("No matching items found")
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


def main():
    """Collects arguments and branches off"""
    # logger = logging.getLogger(__name__)
    migrate_pickle_detection()
    parser = argparse.ArgumentParser()
    # TODO support turning off aliases
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
    args = parser.parse_args()
    # console.print(args.list)
    if args.remove_prepared_jobs is True:

        remove_pickle()
        console.print("Removed the jobs.")
        # exit(0)
    elif args.run_prepared_jobs is True:
        # read pickle as list of BatchJobs
        jobs = parse_pickle()
        if jobs is not None and len(jobs) > 0:
            login()
            print_running_jobs(jobs)
            for job in jobs:
                job.run()
            # Remove the pickle afterwards
            remove_pickle()
    else:
        if args.list is None:
            console.print("Got no QIDs. Quitting")
            exit(0)
        task: Task = select_task()
        if task is None:
            raise ValueError("Got no task")
        jobs = process_user_supplied_qids_into_batch_jobs(args=args, task=task)
        if args.prepare_jobs:
            for job in jobs:
                add_to_pickle(job)
            console.print(f"{len(jobs)} jobs prepared. You can run them "
                          f"non-interactively e.g. on the Toolforge "
                          f"Kubernetes cluster using --run-prepared-jobs. "
                          f"See https://phabricator.wikimedia.org/T285944 "
                          f"for details")
        else:
            login()
            print_running_jobs(jobs)
            for job in jobs:
                job.run()


if __name__ == "__main__":
    main()
