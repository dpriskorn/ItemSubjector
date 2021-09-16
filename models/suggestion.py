import logging
from typing import List
from urllib.parse import quote

from helpers.console import print_search_strings_table
from models.ngram import NGram
from models.wikidata import Item


class Suggestion:
    item: Item = None
    ngram: NGram = None
    search_strings: List[str] = None

    def __init__(self,
                 item: Item = None,
                 ngram: NGram = None):
        if item is not None:
            self.item = item
        if ngram is not None:
            self.ngram: NGram = ngram
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
        # logger = logging.getLogger(__name__)
        self.search_strings: List[str] = [self.item.label]
        if self.item.aliases is not None:
            for alias in self.item.aliases:
                # logger.debug(f"extracting alias:{alias}")
                self.search_strings.append(alias)
        # logger.debug(f"search_strings:{self.search_strings}")
        print_search_strings_table(self.search_strings)

