import argparse
from unittest import TestCase

from src.models.suggestion import Suggestion
from src.models.wikimedia.wikidata.sparql_item import SparqlItem, Value
from src.tasks import tasks


class TestSuggestion(TestCase):
    def test_extract_search_strings(self):
        item = SparqlItem(
            item=Value(value="Q407541"), itemLabel=Value(value="fentanyl")
        )
        item.validate_qid_and_copy_label()
        suggestion = Suggestion(
            item=item,
            task=tasks[0],
            args=argparse.Namespace(
                no_aliases=dict(no_aliases=False),
                show_search_urls=dict(show_search_urls=False),
            ),
        )
        suggestion.extract_search_strings()
        # suggestion.print_search_strings()
        if not len(suggestion.search_strings) == 1:
            self.fail()

    def test_extract_search_strings_with_problematic_alias(self):
        """This has a problematic alias "thrush" which is also a bird"""
        item = SparqlItem(
            item=Value(value="Q273510"), itemLabel=Value(value="candidadis")
        )
        item.validate_qid_and_copy_label()
        item.fetch_label_and_description_and_aliases(task=tasks[0])
        suggestion = Suggestion(
            item=item,
            task=tasks[0],
            args=argparse.Namespace(
                no_aliases=dict(no_aliases=False),
                show_search_urls=dict(show_search_urls=False),
            ),
        )
        suggestion.extract_search_strings()
        suggestion.print_search_strings()
        print(len(suggestion.search_strings))
        assert len(suggestion.search_strings) == 10
