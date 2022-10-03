from __future__ import annotations

import argparse
from typing import Set
from urllib.parse import quote

from rich.table import Table

from src.models.task import Task
from src.helpers.console import console
from src.models.batch_jobs import BatchJobs
from src.helpers.cleaning import clean_rich_formatting
from src.helpers.console import press_enter_to_continue
from src.models.items import Items


def print_best_practice(task: Task):
    if task.best_practice_information:
        console.print(task.best_practice_information)
        press_enter_to_continue()


def print_search_strings_table(
    args: argparse.Namespace = None, search_strings: Set[str] = None
):
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
            table.add_row(
                string, f"https://www.wikidata.org/w/index.php?search={quote(string)}"
            )
        else:
            table.add_row(string)
    console.print(table)


def print_found_items_table(args: argparse.Namespace = None, items: Items = None):
    if args is None:
        raise ValueError("args was None")
    if items is None:
        raise ValueError("items was None")
    if items.sparql_items is None:
        raise ValueError("items.sparql_items was None")
    table = Table(title="Matched items found")
    if len(items.sparql_items) < 1000:
        list_to_show = items.sparql_items[0:50]
    else:
        # Show 1 sample for each 20 items in the sparql_items
        list_to_show = items.sparql_items[0 : int(len(items.sparql_items) / 20)]
    if len(items.sparql_items) > 4000:
        console.print(
            "[red]Warning: This is a very large batch, please proceed with caution[/red]"
        )
        press_enter_to_continue()
    table.add_column(
        f"Showing a random subset of {len(list_to_show)} "
        f"items, please review as many as possible for false "
        f"positives and reject the batch if you find any."
    )
    if getattr(args, "show_item_urls", False):
        table.add_column(f"Wikidata URL")
    for item in list_to_show:
        if item.label is None:
            raise ValueError("main_subject_item.label was None")
        if getattr(args, "show_item_urls", False):
            label = clean_rich_formatting(item.label)
            table.add_row(label, item.url)
        else:
            table.add_row(item.label)
    console.print(table)


def print_finished():
    console.print("All jobs finished successfully")


def print_job_statistics(batchjobs: BatchJobs = None):
    if not batchjobs:
        raise ValueError("jobs was None")
    if not batchjobs.jobs:
        raise ValueError("batchjobs.jobs was None")
    if not isinstance(batchjobs.jobs, list):
        raise ValueError("jobs was not a sparql_items")
    if not len(batchjobs.jobs):
        console.print("The jobs sparql_items is empty")
    else:
        total_number_of_queries = sum([job.number_of_queries for job in batchjobs.jobs])
        total_number_of_items = sum(
            len(job.main_subject_item.items.sparql_items)
            for job in batchjobs.jobs
            if batchjobs.jobs
            and job
            and job.main_subject_item.items
            and job.main_subject_item.items.sparql_items
        )
        console.print(
            f"The jobs sparql_items now contain a total of {len(batchjobs.jobs)} "  # type: ignore
            f"jobs with a total of "
            f"{total_number_of_items} items found from "
            f"{total_number_of_queries} queries"
        )
