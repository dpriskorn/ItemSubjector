from unittest import TestCase

from src import console
from src.models.wikimedia.wikidata.sparql_item import SparqlItem, Value


class TestSparqlItem(TestCase):
    def test_is_in_blocklist(self):
        item = SparqlItem(
            item=Value(value="Q28196260"), itemLabel=Value(value="alcohol")
        )
        item.validate_qid_and_copy_label()
        console.print(item.dict())
        if not item.is_in_blocklist():
            self.fail()
