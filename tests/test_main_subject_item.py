import argparse
from unittest import TestCase

from src.models.wikimedia.wikidata.item.main_subject import MainSubjectItem
from src.tasks import tasks


class TestMainSubjectItem(TestCase):
    def test_extract_search_strings(self):
        msi = MainSubjectItem(
            id="Q407541",
            label="fentanyl",
            task=tasks[0],
            args=argparse.Namespace(
                no_aliases=dict(no_aliases=False),
                show_search_urls=dict(show_search_urls=False),
            ),
        )
        msi.__extract_search_strings__()
        if not len(msi.search_strings) == 1:
            self.fail()

    def test_extract_search_strings_with_problematic_alias(self):
        # Note this will fail if anyone adds or remove an alias on the item.
        msi = MainSubjectItem(
            id="Q273510",
            task=tasks[0],
            args=argparse.Namespace(
                no_aliases=dict(no_aliases=False),
                show_search_urls=dict(show_search_urls=False),
            ),
        )
        msi.__fetch_label_and_description_and_aliases__()
        msi.__extract_search_strings__()
        msi.print_search_strings()
        print(len(msi.search_strings))
        assert len(msi.search_strings) == 10
