import argparse
from typing import List
from urllib.parse import quote

from rich.console import Console
from rich.table import Table

from models.batch_job import BatchJob
from models.task import Task

console = Console()


def ask_yes_no_question(message: str):
    # https://www.quora.com/
    # I%E2%80%99m-new-to-Python-how-can-I-write-a-yes-no-question
    # this will loop forever
    while True:
        answer = console.input(message + ' [Y/Enter/n]: ')
        if len(answer) == 0 or answer[0].lower() in ('y', 'n'):
            if len(answer) == 0:
                return True
            else:
                # the == operator just returns a boolean,
                return answer[0].lower() == 'y'


def print_keep_an_eye_on_wdqs_lag():
    console.print("Please keep an eye on the lag of the WDQS cluster here and avoid "
                  "working if it is over a few minutes.\n"
                  "https://grafana.wikimedia.org/d/000000489/wikidata-query-service?"
                  "orgId=1&viewPanel=8&from=now-30m&to=now&refresh=1d "
                  "You can see if any lagging servers are pooled here\n"
                  "https://config-master.wikimedia.org/pybal/eqiad/wdqs\n"
                  "If any enabled servers are lagging more than 5-10 minutes "
                  "you can search phabricator for open tickets to see if the team is on it.\n"
                  "If you don't find any feel free to create a new ticket like this:\n"
                  "https://phabricator.wikimedia.org/T291621")


def press_enter_to_start():
    console.input("Press Enter to start.")


def print_best_practice(task: Task):
    if task.best_practice_information is not None:
        console.print(task.best_practice_information)
        press_enter_to_start()


def print_search_strings_table(args: argparse.Namespace = None,
                               search_strings: List[str] = None):
    if args is None:
        raise ValueError("args was None")
    if search_strings is None:
        raise ValueError("search strings was None")
    table = Table(title="Search strings")
    table.add_column(f"Extracted the following {len(search_strings)} search strings")
    if args.show_search_urls:
        table.add_column(f"Wikidata search URL")
    for string in search_strings:
        if args.show_search_urls:
            table.add_row(string, f"https://www.wikidata.org/w/index.php?search={quote(string)}")
        else:
            table.add_row(string)
    console.print(table)


def print_found_items_table(args: argparse.Namespace = None,
                            task: Task = None):
    if args is None:
        raise ValueError("args was None")
    if task is None:
        raise ValueError("task was None")
    table = Table(title="Matched items found")
    table.add_column("Showing only a random subset of 50 items if more are found")
    if args.show_item_urls:
        table.add_column(f"Wikidata URL")
    for item in task.items.list[0:50]:
        if args.show_item_urls:
            table.add_row(item.label, item.url())
        else:
            table.add_row(item.label)
    console.print(table)


def ask_add_to_job_queue(job: BatchJob = None):
    return ask_yes_no_question(f"Do you want to add this job for "
                               f"[magenta]{job.suggestion.item.label}: "
                               f"{job.suggestion.item.description}[/magenta] with "
                               f"{len(job.task.items.list)} items to the queue? (see {job.suggestion.item.url()})")


def print_running_jobs(jobs: List[BatchJob] = None):
    if jobs is None:
        raise ValueError("jobs was None")
    console.print(f"Running {len(jobs)} job(s) with a total of "
                  f"{sum(len(job.task.items.list) for job in jobs)} items "
                  f"non-interactively now. You can take a "
                  f"coffee break and lean back :)")


def print_finished():
    console.print("All jobs finished successfully")


