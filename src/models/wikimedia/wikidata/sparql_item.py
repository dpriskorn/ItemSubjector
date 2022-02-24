from pydantic import BaseModel

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
