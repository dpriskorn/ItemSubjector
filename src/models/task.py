from typing import Union, Optional

from src.helpers.enums import SupportedLanguageCode, TaskIds


# console-menu does not support dataclass (yet)
# @dataclass
class Task:
    """This class holds the tasks presented to the
    user in the menu and related data"""
    best_practice_information: Union[str, None] = None
    id: Optional[TaskIds] = None
    label: Optional[str] = None
    language_code: Optional[SupportedLanguageCode] = None
    number_of_queries_per_search_string = 1

    def __init__(self,
                 best_practice_information: str = None,
                 id: TaskIds = None,
                 label: str = None,
                 language_code: SupportedLanguageCode = None,
                 number_of_queries_per_search_string: int = None):
        if id is None:
            raise ValueError("Got no id")
        if label is None:
            raise ValueError("Got no label")
        if language_code is None:
            raise ValueError("Got no language_code")
        self.id = id
        self.label = label
        self.language_code = language_code
        self.best_practice_information = best_practice_information
        if number_of_queries_per_search_string is not None:
            self.number_of_queries_per_search_string = number_of_queries_per_search_string

    def __str__(self):
        return f"{self.label}"
