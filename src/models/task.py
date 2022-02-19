from typing import Union

from pydantic import BaseModel

from src.helpers.enums import SupportedLanguageCode, TaskIds


class Task(BaseModel):
    """This class holds the tasks presented to the
    user in the menu and related data"""
    best_practice_information: Union[str, None]
    id: TaskIds
    label: str
    language_code: SupportedLanguageCode
    number_of_queries_per_search_string = 1

    # def __init__(self,
    #              best_practice_information: str = None,
    #              id: TaskIds = None,
    #              label: str = None,
    #              language_code: SupportedLanguageCode = None,
    #              number_of_queries_per_search_string: int = None):
    #     if id is None:
    #         raise ValueError("Got no id")
    #     if label is None:
    #         raise ValueError("Got no label")
    #     if language_code is None:
    #         raise ValueError("Got no language_code")
    #     self.id = id
    #     self.label = label
    #     self.language_code = language_code
    #     self.best_practice_information = best_practice_information
    #     if number_of_queries_per_search_string is not None:
    #         self.number_of_queries_per_search_string = number_of_queries_per_search_string

    def __str__(self):
        return f"{self.label}"
