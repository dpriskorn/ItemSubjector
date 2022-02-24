from __future__ import annotations

import argparse
from typing import List, TYPE_CHECKING
from urllib.parse import quote

from rich.console import Console
from rich.table import Table

from src.helpers.cleaning import clean_rich_formatting
from src.models.batch_job import BatchJob
from src.models.batch_jobs import BatchJobs

if TYPE_CHECKING:
    from src.models.items import Items
    from src.models.task import Task

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


def press_enter_to_continue():
    console.input("Press Enter to continue.")


def print_best_practice(task: Task):
    if task.best_practice_information is not None:
        console.print(task.best_practice_information)
        press_enter_to_continue()


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
                            items: Items = None):
    if args is None:
        raise ValueError("args was None")
    if items is None:
        raise ValueError("items was None")
    if items.list is None:
        raise ValueError("items.list was None")
    table = Table(title="Matched items found")
    if len(items.list) < 1000:
        list_to_show = items.list[0:50]
    else:
        # Show 1 sample for each 20 items in the list
        list_to_show = items.list[0:int(len(items.list) / 20)]
    if len(items.list) > 4000:
        console.print("[red]Warning: This is a very large batch, please proceed with caution[/red]")
        press_enter_to_continue()
    table.add_column(f"Showing a random subset of {len(list_to_show)} "
                     f"items, please review as many as possible for false "
                     f"positives and reject the batch if you find any.")
    if args.show_item_urls:
        table.add_column(f"Wikidata URL")
    for item in list_to_show:
        if item.label is None:
            raise ValueError("item.label was None")
        if args.show_item_urls:
            label = clean_rich_formatting(item.label)
            table.add_row(label, item.url())
        else:
            table.add_row(item.label)
    console.print(table)


def ask_add_to_job_queue(job: BatchJob = None):
    if job is None:
        raise ValueError("job was None")
    if job.suggestion.item is None:
        raise ValueError("job.suggestion.item was None")
    if job.suggestion.item.label is None:
        raise ValueError("job.suggestion.item.label was None")
    if job.suggestion.item.description is None:
        job.suggestion.item.description = ""
    if job.items.list is None:
        raise ValueError("job.items.list was None")
    return ask_yes_no_question(f"Do you want to add this job for "
                               f"[magenta]{job.suggestion.item.label}: "
                               f"{job.suggestion.item.description}[/magenta] with "
                               f"{len(job.items.list)} items to the queue? (see {job.suggestion.item.url()})")


def print_finished():
    console.print("All jobs finished successfully")


def print_job_statistics(batchjobs: BatchJobs = None):
    if batchjobs is None:
        raise ValueError("jobs was None")
    if batchjobs.jobs is None:
        raise ValueError("batchjobs.jobs was None")
    if not isinstance(batchjobs.jobs, list):
        raise ValueError("jobs was not a list")
    if len(batchjobs.jobs) == 0:
        console.print("The jobs list is empty")
    else:
        console.print(f"The jobs list now contain a total of {len(batchjobs.jobs)} "
                      f"jobs with a total of "
                      f"{sum(len(job.items.list) for job in batchjobs.jobs if batchjobs.jobs is not None and job is not None)} items")


def ask_discard_existing_job_pickle():
    return ask_yes_no_question("A prepared list of jobs already exist, "
                               "do you want to delete it?")
