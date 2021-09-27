import logging
from typing import List

from consolemenu import SelectionMenu

from src.models.suggestion import Suggestion
from src.models.wikidata import WikimediaLanguageCode, Item

# def select_lexical_category():
#     logger = logging.getLogger(__name__)
#     menu = SelectionMenu(WikidataLexicalCategory.__members__.keys(), "Select a lexical category")
#     menu.show()
#     menu.join()
#     selected_lexical_category_index = menu.selected_option
#     category_mapping = {}
#     for index, item in enumerate(WikidataLexicalCategory):
#         category_mapping[index] = item
#     selected_lexical_category = category_mapping[selected_lexical_category_index]
#     logger.debug(f"selected:{selected_lexical_category_index}="
#                  f"{selected_lexical_category}")
#     return selected_lexical_category
from src.tasks import tasks


def select_language():
    logger = logging.getLogger(__name__)
    menu = SelectionMenu(WikimediaLanguageCode.__members__.keys(), "Select a language")
    menu.show()
    menu.join()
    selected_language_index = menu.selected_option
    mapping = {}
    for index, item in enumerate(WikimediaLanguageCode):
        mapping[index] = item
    selected_language = mapping[selected_language_index]
    logger.debug(f"selected:{selected_language_index}="
                 f"{selected_language}")
    return selected_language


def select_task():
    logger = logging.getLogger(__name__)
    menu = SelectionMenu(tasks, "Select a task")
    menu.show()
    menu.join()
    task_index = menu.selected_option
    selected_task = tasks[task_index]
    logger.debug(f"selected:{task_index}="
                 f"{selected_task}")
    return selected_task


def select_suggestion(suggestions: List[Suggestion] = None,
                      item: Item = None):
    if item is None or suggestions is None:
        raise ValueError("Did not get what we need")
    logger = logging.getLogger(__name__)
    menu = SelectionMenu(suggestions, f"Does any of these fit the label \n'{item.label}'")
    menu.show()
    menu.join()
    selected_index = menu.selected_option
    selected_suggestion = None
    if selected_index == len(suggestions) + 1:
        logger.debug("The user choose to skip")
    else:
        selected_suggestion = tasks[selected_index]
        logger.debug(f"selected:{selected_index}="
                     f"{selected_suggestion}")
    return selected_suggestion
