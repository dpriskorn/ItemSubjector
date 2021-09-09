import logging

from consolemenu import SelectionMenu

from models.wikidata import WikimediaLanguageCode


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
from tasks import tasks


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
