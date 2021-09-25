from dataclasses import dataclass
from typing import Union

from helpers.enums import SupportedLanguageCode, TaskIds


# console-menu does not support dataclass (yet)
# @dataclass
class Task:
    """This class holds the tasks presented to the
    user in the menu and related data"""
    best_practice_information: Union[str, None] = None
    id: TaskIds = None
    label: str = None
    language_code: SupportedLanguageCode = None
    question: str = None

    def __init__(self,
                 best_practice_information: str = None,
                 id: TaskIds = None,
                 label: str = None,
                 language_code: SupportedLanguageCode = None,
                 question: str = None):
        if id is None:
            raise ValueError("Got no id")
        if label is None:
            raise ValueError("Got no label")
        if question is None:
            raise ValueError("Got no question")
        if language_code is None:
            raise ValueError("Got no language_code")
        self.id = id
        self.label = label
        self.question = question
        self.language_code = language_code
        self.best_practice_information = best_practice_information

    def __str__(self):
        return f"{self.label}"
