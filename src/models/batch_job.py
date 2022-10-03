from pydantic import BaseModel

from src.models.wikimedia.wikidata.item.main_subject import MainSubjectItem


class BatchJob(BaseModel):
    """Models a batch job intended to be run non-interactively"""

    main_subject_item: MainSubjectItem
    number_of_queries: int
