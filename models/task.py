from typing import Union

from helpers.enums import SupportedLanguageCode
# console-menu does not support dataclass (yet)
# @dataclass
from models.wikidata import Items


class Task:
    """This class holds the tasks presented to the
    user in the menu and related data"""
    best_practice_information: Union[str, None] = None
    label: str = None
    language_code: SupportedLanguageCode = None
    question: str = None
    items: Items = None

    def __init__(self,
                 best_practice_information: str = None,
                 items: Items = None,
                 label: str = None,
                 language_code: SupportedLanguageCode = None,
                 question: str = None):
        if label is None:
            raise ValueError("Got no label")
        if question is None:
            raise ValueError("Got no question")
        if language_code is None:
            raise ValueError("Got no language_code")
        if items is None:
            raise ValueError("Got no items")
        self.id = id
        self.label = label
        self.question = question
        self.language_code = language_code
        self.best_practice_information = best_practice_information
        self.items = items

    def __str__(self):
        return f"{self.label}"
