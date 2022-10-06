import logging
from typing import List

from consolemenu import SelectionMenu  # type: ignore

from src.models.wikimedia.wikidata.item import Item
from src.models.wikimedia.wikidata.item.main_subject import MainSubjectItem
from src.tasks import Task

logger = logging.getLogger(__name__)


def select_suggestion(suggestions: List[MainSubjectItem], item: Item):
    if not item or not item.id or not suggestions:
        raise ValueError("Did not get what we need")
    menu = SelectionMenu(
        suggestions, f"Does any of these fit the label \n'{item.label}'"
    )
    menu.show()
    menu.join()
    selected_index = menu.selected_option
    # selected_suggestion = None
    if selected_index > (len(suggestions) - 1):
        logger.debug("The user choose to skip")
        return None
    else:
        from src.tasks import tasks

        selected_suggestion = tasks[selected_index]
        logger.debug(f"selected:{selected_index}=" f"{selected_suggestion}")
        return selected_suggestion


def select_task() -> Task:
    # TODO use questionary here?
    from src.tasks import tasks

    labels = [task.label for task in tasks]
    # console.print(labels)
    menu = SelectionMenu(labels, "Select a task")
    menu.show()
    menu.join()
    task_index = menu.selected_option
    if task_index > (len(tasks) - 1):
        logger.info("Got exit")
        exit(0)
    selected_task = tasks[task_index]
    logger.debug(f"selected:{task_index}=" f"{selected_task}")
    return selected_task


# def select_language():
#     logger = logging.getLogger(__name__)
#     menu = SelectionMenu(WikimediaLanguageCode.__members__.keys(), "Select a language")
#     menu.show()
#     menu.join()
#     selected_language_index = menu.selected_option
#     mapping = {}
#     for index, main_subject_item in enumerate(WikimediaLanguageCode):
#         mapping[index] = main_subject_item
#     selected_language = mapping[selected_language_index]
#     logger.debug(f"selected:{selected_language_index}="
#                  f"{selected_language}")
#     return selected_language

# def select_lexical_category():
#     logger = logging.getLogger(__name__)
#     menu = SelectionMenu(WikidataLexicalCategory.__members__.keys(), "Select a lexical category")
#     menu.show()
#     menu.join()
#     selected_lexical_category_index = menu.selected_option
#     category_mapping = {}
#     for index, main_subject_item in enumerate(WikidataLexicalCategory):
#         category_mapping[index] = main_subject_item
#     selected_lexical_category = category_mapping[selected_lexical_category_index]
#     logger.debug(f"selected:{selected_lexical_category_index}="
#                  f"{selected_lexical_category}")
#     return selected_lexical_category
