import logging
from typing import Dict

from wikibaseintegrator.wbi_helpers import execute_sparql_query  # type: ignore

from src.helpers.console import console
from src.models.items import Items
from src.models.wikimedia.wikidata.query.preprint_article import PreprintArticleQuery
from src.models.wikimedia.wikidata.query.published_article import PublishedArticleQuery

logger = logging.getLogger(__name__)


class ScholarlyArticleItems(Items):
    """This supports both published peer reviewed articles and preprints"""

    cirrussearch_parameters: str = ""
    query: str = ""
    results: Dict = {}

    def fetch_based_on_label(self):
        self.execute_queries()
        self.print_total_items()

    def execute_queries(self):
        # Fetch all items matching the search strings
        for search_string in self.main_subject_item.search_strings:
            published_article_query = PublishedArticleQuery(
                search_string=search_string,
                main_subject_item=self.main_subject_item,
                cirrussearch_parameters=self.cirrussearch_parameters,
            )
            published_article_query.get_results()
            # https://pythonexamples.org/python-append-list-to-another-list/
            self.sparql_items.extend(published_article_query.items)
            published_article_query.print_number_of_results()
            # preprints
            # We don't use CirrusSearch in this query because we can do it more easily in
            # SPARQL on a small subgraph like this
            # find all items that are ?main_subject_item wdt:P31/wd:P279* wd:Q1266946
            # minus the Qid we want to add
            preprint_query = PreprintArticleQuery(
                search_string=search_string, main_subject_item=self.main_subject_item
            )
            preprint_query.get_results()
            preprint_query.print_number_of_results()
            self.sparql_items.extend(preprint_query.items)

    def print_total_items(self):
        console.print(f"Got a total of {len(self.sparql_items)} items")
