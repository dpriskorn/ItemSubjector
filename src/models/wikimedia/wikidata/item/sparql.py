from pydantic import BaseModel

import config
from src.models.wikimedia.wikidata.entiyt_id import EntityId
from src.models.wikimedia.wikidata.item import Item


class Value(BaseModel):
    value: str


class SparqlItem(Item):
    """This class models the data we get from SPARQL"""

    item: Value
    itemLabel: Value

    def validate_qid_and_copy_label(self):
        self.id = str(EntityId(self.item.value))
        self.label = self.itemLabel.value

    def is_in_blocklist(self) -> bool:
        if self.id is None:
            raise ValueError("did not get an id")
        if config.blocklist_for_scholarly_items is None:
            raise ValueError(
                "config.blocklist_for_scholarly_items was None, please fix"
            )
        if self.id in config.blocklist_for_scholarly_items:
            return True
        else:
            return False
