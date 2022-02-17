from typing import Optional

from src.models.wikidata.entiyt_id import EntityID


class ForeignID:
    id: Optional[str]
    property: Optional[str]  # This is the property with type ExternalId
    source_item_id: Optional[str]  # This is the Q-item for the source

    def __init__(self,
                 id: Optional[str] = None,
                 property: Optional[str] = None,
                 source_item_id: Optional[str] = None):
        self.id = id
        if property is None:
            raise ValueError("property was None")
        self.property = str(EntityID(property))
        if source_item_id is None:
            raise ValueError("source_item_id was None")
        self.source_item_id = str(EntityID(source_item_id))
