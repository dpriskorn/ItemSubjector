from dataclasses import dataclass
from enum import Enum

from src.models.wikidata import EntityID


class QuickStatementsNamespaceLetters(Enum):
    PROPERTY = "P"
    ITEM = "Q"
    LEXEME = "L"
    REFERENCE = "S"


class QuickStatementsID(EntityID):
    letter = QuickStatementsNamespaceLetters


@dataclass
class QuickStatementsCommandVersion1:
    """This models the simple line-based QS commands

    For now we only support QID-values

    Q1\tP1\tQ1"""
    target: QuickStatementsID = None
    property: QuickStatementsID = None
    value: QuickStatementsID = None
    last: bool = False

    def __str__(self):
        if self.last is True:
            return f"LAST\t{self.property}\t{self.value}"
        else:
            return f"{self.target}\t{self.property}\t{self.value}"
