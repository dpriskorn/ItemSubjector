from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from src.models.wikimedia.wikidata.entiyt_id import EntityId


class QuickStatementsCommandVersion1(BaseModel):
    """This models the simple line-based QS commands

    For now we only support QID-values

    Q1\tP1\tQ1"""
    target: Optional[EntityId] = None
    property: Optional[EntityId] = None
    value: Optional[EntityId] = None

    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        return f"{self.target}\t{self.property}\t{self.value}"
