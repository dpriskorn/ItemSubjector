from dataclasses import dataclass

from src.models.wikidata import EntityID


@dataclass
class QuickStatementsCommandVersion1:
    """This models the simple line-based QS commands

    For now we only support QID-values

    Q1\tP1\tQ1"""
    target: EntityID = None
    property: EntityID = None
    value: EntityID = None

    def __str__(self):
        return f"{self.target}\t{self.property}\t{self.value}"
