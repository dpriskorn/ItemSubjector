import argparse
import logging
from typing import List
from urllib.parse import quote

from wikibaseintegrator.datatypes import Item as ItemType

from helpers.calculations import calculate_random_editgroups_hash
from helpers.console import print_search_strings_table, console
from models.batch_job import BatchJob
from models.task import Task
from models.wikidata import Item


class Suggestion:
    item: Item = None
    search_strings: List[str] = None
    args: argparse.Namespace = None

    def __init__(self,
                 item: Item = None,
                 args=None):
        if item is None:
            raise ValueError("item was None")
        else:
            self.item = item
        self.args = args
        self.extract_search_strings()

    def __str__(self):
        """Return label and description, the latter cut to 50 chars"""
        if self.item is not None:
            aliases = None
            if self.item.aliases is not None:
                aliases = ', '.join(self.item.aliases)
            return (
                f"label: [bold]{self.item.label}[/bold]\n"
                f"aliases: {aliases}\n"
                f"description: {self.item.description[:70]}\n"
                f"{self.item.url()}\n"
            )
        else:
            raise ValueError("self.item was None")

    def add_to_items(self,
                     task: Task = None,
                     jobs: List[BatchJob] = None,
                     job_count: int = None):
        """Add a suggested QID as main subject on all items that
        have a label that matches one of the search strings for this QID
        We calculate a new edit group hash each time this function is
        called so similar edits are grouped and easily be undone.

        The task hold all the items.
        jobs and job_count are passed here for printing progess to the UI

        This function is non-interactive"""
        logger = logging.getLogger(__name__)
        if task is None:
            raise ValueError("task was None")
        if jobs is None:
            raise ValueError("jobs was None")
        if job_count is None:
            raise ValueError("job count was None")
        if not len(task.items.list) > 0:
            raise ValueError("list of items was 0")
        editgroups_hash: str = calculate_random_editgroups_hash()
        count = 0
        for target_item in task.items.list:
            count += 1
            with console.status(f"Uploading main subject [green]{self.item.label}[/green] to {target_item.label}"):
                input("Press enter to continue")
                main_subject_property = "P921"
                reference = ItemType(
                    "Q69652283",  # inferred from title
                    prop_nr="P887"  # based on heuristic
                )
                statement = ItemType(
                    self.item.id,
                    prop_nr=main_subject_property,
                    references=[reference]
                )
                target_item.upload_one_statement_to_wikidata(
                    statement=statement,
                    summary=f"[[Property:{main_subject_property}]]: [[{self.item.id}]]",
                    editgroups_hash=editgroups_hash
                )
            console.print(f"(job {job_count}/{len(jobs)})(item {count}/{len(task.items.list)}) "
                          f"Added '{self.item.label}' to {target_item.label}: {target_item.url()}")

    def extract_search_strings(self):
        logger = logging.getLogger(__name__)
        if self.args is None:
            raise ValueError("args was None")
        else:
            logger.debug(f"args:{self.args}")
            if self.args.no_aliases is True:
                console.print("Alias matching is turned off")
                no_aliases = True
            else:
                no_aliases = False
        self.search_strings: List[str] = [self.item.label]
        if (
            self.item.aliases is not None and
            no_aliases is False
        ):
            for alias in self.item.aliases:
                # logger.debug(f"extracting alias:{alias}")
                self.search_strings.append(alias)
        # logger.debug(f"search_strings:{self.search_strings}")
        print_search_strings_table(args=self.args,
                                   search_strings=self.search_strings)

    def search_urls(self) -> List[str]:
        urls = []
        for search_string in self.search_strings:
            search_term = quote(f'"{search_string}"')
            urls.append(f"https://www.wikidata.org/w/index.php?search={search_term}")
        return urls
