from __future__ import annotations

import argparse
import logging
from typing import List, Optional, TYPE_CHECKING
from urllib.parse import quote

from pydantic import BaseModel
from wikibaseintegrator.datatypes import Item as ItemType  # type: ignore

import config
from src.helpers.calculations import calculate_random_editgroups_hash
from src.helpers.cleaning import clean_rich_formatting
from src.models.items import Items
from src.models.task import Task
from src.models.wikimedia.wikidata.item import Item

if TYPE_CHECKING:
    from src.models.batch_job import BatchJob


class Suggestion(BaseModel):
    item: Item
    task: Task
    args: argparse.Namespace
    search_strings: Optional[List[str]] = None

    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        """Return label and description, the latter cut to 50 chars"""
        if self.item is not None:
            string = (
                f"label: [bold]{clean_rich_formatting(self.item.label)}[/bold]\n"
                f"aliases: {', '.join(self.item.aliases)}\n"
                f"description: {self.item.description[:70]}\n"
                f"{self.item.url()}\n"
            )
            for url in self.search_urls():
                string = string + f"{url}\n"
            return string

    def add_to_items(
        self, items: Items = None, jobs: List[BatchJob] = None, job_count: int = None
    ):
        """Add a suggested QID as main subject on all items that
        have a label that matches one of the search strings for this QID
        We calculate a new edit group hash each time this function is
        called so similar edits are grouped and easily be undone.

        This function is non-interactive"""
        if items is None:
            raise ValueError("Items was None")
        if items.list is None:
            raise ValueError("items.list was None")
        if jobs is None:
            raise ValueError("jobs was None")
        if job_count is None:
            raise ValueError("job count was None")
        editgroups_hash: str = calculate_random_editgroups_hash()
        count = 0
        for target_item in items.list:
            count += 1
            from src import console

            with console.status(
                f"Uploading main subject "
                f"[green]{clean_rich_formatting(self.item.label)}[/green] "
                f"to {clean_rich_formatting(target_item.label)}"
            ):
                main_subject_property = "P921"
                reference = ItemType(
                    "Q69652283",  # inferred from title
                    prop_nr="P887",  # based on heuristic
                )
                statement = ItemType(
                    self.item.id, prop_nr=main_subject_property, references=[reference]
                )
                target_item.upload_one_statement_to_wikidata(
                    statement=statement,
                    summary=f"[[Property:{main_subject_property}]]: [[{self.item.id}]]",
                    editgroups_hash=editgroups_hash,
                )
            console.print(
                f"(job {job_count}/{len(jobs)})(item {count}/{len(items.list)}) "
                f"Added '{clean_rich_formatting(self.item.label)}' to "
                f"{clean_rich_formatting(target_item.label)}: {target_item.url()}"
            )
            # input("Press enter to continue")

    def extract_search_strings(self):
        def clean_special_symbols(string: str):
            return string.replace("®", "").replace("™", "")

        from src.helpers.console import console

        logger = logging.getLogger(__name__)
        if self.args is None:
            raise ValueError("args was None")
        else:
            logger.debug(f"args:{self.args}")
            if self.args.no_aliases is True:
                from src import console

                console.print("Alias matching is turned off")
                no_aliases = True
            else:
                no_aliases = False
        self.search_strings: List[str] = [clean_special_symbols(self.item.label)]
        if self.item.aliases is not None and no_aliases is False:
            for alias in self.item.aliases:
                # logger.debug(f"extracting alias:{alias}")
                if len(alias) < 5 and alias not in config.list_of_allowed_aliases:
                    console.print(
                        f"Skipping short alias '{alias}' to avoid false positives",
                        style="#FF8000",
                    )
                elif alias in config.list_of_allowed_aliases:
                    console.print(f"Found {alias} in the allow list")
                    self.search_strings.append(clean_special_symbols(alias))
                else:
                    self.search_strings.append(clean_special_symbols(alias))
        # logger.debug(f"search_strings:{self.search_strings}")
        from src.helpers.console import print_search_strings_table

        print_search_strings_table(args=self.args, search_strings=self.search_strings)

    def search_urls(self) -> List[str]:
        if self.search_strings is None:
            raise ValueError("self.search_strings was None")
        urls = []
        for search_string in self.search_strings:
            search_term = quote(f'"{search_string}"')
            urls.append(f"https://www.wikidata.org/w/index.php?search={search_term}")
        return urls
