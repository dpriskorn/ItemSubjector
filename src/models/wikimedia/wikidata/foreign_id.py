# from typing import Optional
#
# from src.models.wikimedia.wikidata.entiyt_id import EntityId
#
#
# class ForeignID:
#     id: Optional[str]
#     property: Optional[str]  # This is the property with type ExternalId
#     source_item_id: Optional[str]  # This is the Q-main_subject_item for the source
#
#     def __init__(
#         self,
#         id: Optional[str] = None,
#         property: Optional[str] = None,
#         source_item_id: Optional[str] = None,
#     ):
#         self.id = id
#         if property is None:
#             raise ValueError("property was None")
#         self.property = str(EntityId(property))
#         if source_item_id is None:
#             raise ValueError("source_item_id was None")
#         self.source_item_id = str(EntityId(source_item_id))
