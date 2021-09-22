import logging
from typing import List
from urllib.parse import quote

from wikibaseintegrator.datatypes import Item as ItemType

from helpers.calculations import calculate_random_editgroups_hash
from helpers.console import print_search_strings_table, console
from helpers.enums import TaskIds
from models.ngram import NGram
from models.task import Task
from models.wikidata import Item, Items


class Suggestion:
    item: Item = None
    ngram: NGram = None
    search_strings: List[str] = None
    task: Task = None
    args = None

    def __init__(self,
                 item: Item = None,
                 ngram: NGram = None,
                 task: Task = None,
                 args=None):
        if item is None:
            raise ValueError("item was None")
        else:
            self.item = item
        if ngram is None:
            raise ValueError("ngram was None")
        else:
            self.ngram: NGram = ngram
        if task is None:
            raise ValueError("task was None")
        else:
            self.task = task
            self.args = args
            self.extract_search_strings()

    def __str__(self):
        """Return label and description, the latter cut to 50 chars"""
        if self.ngram is not None and self.item is not None:
            return (
                f"n-gram: [green][bold]{self.ngram.label}[/bold][/green]\n"
                f"label: [bold]{self.item.label}[/bold]\n"
                f"aliases: {', '.join(self.item.aliases)}\n"
                f"description: {self.item.description[:70]}\n"
                f"{self.item.url()}\n"
                f"{self.ngram_search_url()}"
            )
        else:
            if self.item is not None:
                string = (
                    f"label: [bold]{self.item.label}[/bold]\n"
                    f"aliases: {', '.join(self.item.aliases)}\n"
                    f"description: {self.item.description[:70]}\n"
                    f"{self.item.url()}\n"
                )
                for url in self.search_urls():
                    string = string + f"{url}\n"
                return string

    def search_urls(self) -> List[str]:
        urls = []
        for search_string in self.search_strings:
            search_term = quote(f'"{search_string}"')
            urls.append(f"https://www.wikidata.org/w/index.php?search={search_term}")
        return urls

    def ngram_search_url(self):
        search_term = quote(f'"{self.ngram.label}"')
        return f"https://www.wikidata.org/w/index.php?search={search_term}"

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
        # Turn off alias matching for Riksdagen documents for now
        if (
            self.item.aliases is not None and
            no_aliases is False and
            self.task.id != TaskIds.RIKSDAGEN_DOCUMENTS
        ):
            for alias in self.item.aliases:
                # logger.debug(f"extracting alias:{alias}")
                self.search_strings.append(alias)
        # logger.debug(f"search_strings:{self.search_strings}")
        print_search_strings_table(self.search_strings)

    def add_to_items(self, items: Items = None):
        """Add a suggested QID as main subject on all items that
        have a label that matches one of the search strings for this QID
        We calculate a new edit group hash each time this function is
        called so similar edits are grouped and easily be undone.

        This function is non-interactive"""
        if items is None:
            raise ValueError("Items was None")
        editgroups_hash: str = calculate_random_editgroups_hash()
        count = 0
        for target_item in items.list:
            count += 1
            with console.status(f"Uploading main subject [green]{self.item.label}[/green] to {target_item.label}"):
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
            console.print(f"({count}/{len(items.list)}) "
                          f"Added '{self.item.label}' to {target_item.label}: {target_item.url()}")
            # input("Press enter to continue")


