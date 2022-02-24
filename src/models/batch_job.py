from pydantic import BaseModel

from src.models.items import Items
from src.models.suggestion import Suggestion


class BatchJob(BaseModel):
    """Models a batch job intended to be run non-interactively"""

    suggestion: Suggestion
    items: Items
