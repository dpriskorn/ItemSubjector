from dataclasses import dataclass
from typing import Optional

from src.models.wikidata.entiyt_id import EntityID


@dataclass
class QuickStatementsCommandVersion1:
    """This models the simple line-based QS commands

    For now we only support QID-values

    Q1\tP1\tQ1"""
    target: Optional[EntityID] = None
    property: Optional[EntityID] = None
    value: Optional[EntityID] = None

    def __str__(self):
        return f"{self.target}\t{self.property}\t{self.value}"
