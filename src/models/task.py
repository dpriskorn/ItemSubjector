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

    def __str__(self):
        return f"{self.label}"
