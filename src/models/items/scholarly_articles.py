import logging
from typing import Dict

from wikibaseintegrator.wbi_helpers import execute_sparql_query  # type: ignore

from src.models.items import Items
from src.models.wikimedia.wikidata.query.preprint_article import PreprintArticleQuery
from src.models.wikimedia.wikidata.query.published_article import PublishedArticleQuery
from src.models.wikimedia.wikidata.query.thesis import ThesisQuery

logger = logging.getLogger(__name__)


class ScholarlyArticleItems(Items):
    """This supports both published peer reviewed articles, thesis' and preprints"""

    cirrussearch_parameters: str = ""
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
            preprint_query = PreprintArticleQuery(
                search_string=search_string, main_subject_item=self.main_subject_item
            )
            preprint_query.get_results()
            preprint_query.print_number_of_results()
            self.sparql_items.extend(preprint_query.items)
            thesis_query = ThesisQuery(
                search_string=search_string, main_subject_item=self.main_subject_item
            )
            thesis_query.get_results()
            thesis_query.print_number_of_results()
            self.sparql_items.extend(thesis_query.items)
