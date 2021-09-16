import argparse
import logging

from wikibaseintegrator import wbi_login, wbi_config
from wikibaseintegrator.datatypes import Item as ItemType

import config
from helpers.calculations import calculate_random_editgroups_hash
from helpers.console import console, ask_yes_no_question, introduction, print_ngram_table, \
    print_scholarly_articles_best_practice_information, print_riksdagen_documents_best_practice_information, \
    print_found_items_table, ask_continue_with_the_rest
from helpers.enums import TaskIds
from helpers.menus import select_task
from models.ngram import NGram
from models.riksdagen_documents import RiksdagenDocumentItems
from models.scholarly_articles import ScholarlyArticleItems
from models.suggestion import Suggestion
from models.task import Task
from models.wikidata import Item
from tasks import tasks

logging.basicConfig(level=logging.WARNING)

# pseudo code
# let user choose what to work on ie.
# let user choose language and subgraph
# e.g. Swedish documents from Riksdagen
# e.g. English scientific articles

# loop:
# get some labels
# let the user chose 1 meaningful match from our home cooked NER
# download all items without main subject matching the matched entity
# and with the entity label in the item label
# upload main subject to all


def add_suggestion_to_items(suggestion: Suggestion = None,
                            task: Task = None):
    """Add a suggested QID as main subject on all items that
    have a label that matches one of the search strings for this QID
    We calculate a new edit group hash each time this function is
    called so similar edits are grouped and easily be undone."""
    if suggestion is None:
        raise ValueError("suggestion was None")
    if task is None:
        raise ValueError("task was None")
    with console.status(f'Fetching items with labels that have one of '
                        f'the search strings by running a total of '
                        f'{len(suggestion.search_strings)} queries on WDQS...'):
        if task.id == TaskIds.SCHOLARLY_ARTICLES:
            items = ScholarlyArticleItems()
        elif task.id == TaskIds.RIKSDAGEN_DOCUMENTS:
            items = RiksdagenDocumentItems()
        else:
            raise ValueError(f"{task.id} was not recognized")
        items.fetch_based_on_label(suggestion=suggestion,
                                   task=task)
    if len(items.list) > 0:
        # Randomize the list
        items.random_shuffle_list()
        print_found_items_table(items=items)
        ask_continue_with_the_rest()
        editgroups_hash: str = calculate_random_editgroups_hash()
        for item in items.list:
            with console.status(f"Uploading main subject [green]{suggestion.item.label}[/green] to {item.label}"):
                main_subject_property = "P921"
                reference = ItemType(
                    "Q69652283",  # inferred from title
                    prop_nr="P887"  # based on heuristic
                )
                statement = ItemType(
                    suggestion.item.id,
                    prop_nr=main_subject_property,
                    references=[reference]
                )
                item.upload_one_statement_to_wikidata(
                    statement=statement,
                    summary=f"[[Property:{main_subject_property}]]: [[{suggestion.item.id}]]",
                    editgroups_hash=editgroups_hash
                )
            console.print(f"Added '{suggestion.item.label}' to {item.label}: {item.url()}")
            # input("Press enter to continue")
    else:
        console.print("No matching items found")


def process_ngrams(results):
    suggestions = []
    with console.status("Searching the Wikidata API for entities matching the found n-grams..."):
        for result in results:
            ngram = NGram(
                label=result,
                frequency=results[result]
            )
            suggestion = ngram.recognize_named_entity()
            if suggestion is not None:
                suggestions.append(suggestion)
    console.print("[bold,green]Found the following candidates:")
    for suggestion in suggestions:
        answer = ask_yes_no_question(f"{str(suggestion)}\n"
                                     f"Is this a valid main subject?")
        if answer:
            add_suggestion_to_items(suggestion=suggestion)
        else:
            console.print("Skipping this suggestion")
        console.print("\n")


def process_user_supplied_qids(args=None, task: Task = None):
    """Given a list of QIDs, we go through
    them and call add_suggestion_to_items() on each one"""
    if args is None:
        raise ValueError("args was None")
    if task is None:
        raise ValueError("task was None")
    if task.id == TaskIds.SCHOLARLY_ARTICLES:
        print_scholarly_articles_best_practice_information()
    elif task.id == TaskIds.RIKSDAGEN_DOCUMENTS:
        print_riksdagen_documents_best_practice_information()
    else:
        raise ValueError(f"taskid {task.id} not recognized")
    login()
    for qid in args.list:
        item = Item(
            id=qid,
            task=task
        )
        console.print(f"Working on {item}")
        # generate suggestion with all we need
        suggestion = Suggestion(
            item=item,
            ngram=NGram(
                label=item.label,
                frequency=None
            ),
            task=task
        )
        add_suggestion_to_items(suggestion=suggestion,
                                task=task)


def login():
    with console.status("Logging in with WikibaseIntegrator..."):
        config.login_instance = wbi_login.Login(
            auth_method='login',
            user=config.username,
            password=config.password,
            debug=False
        )
        # Set User-Agent
        wbi_config.config["USER_AGENT_DEFAULT"] = config.user_agent


def main():
    # logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()
    # TODO support turning off aliases
    parser.add_argument('-l', '--list',
                        nargs='+',
                        help=('List of QIDs that are to be added as '
                              'main subjects on scientific articles. '
                              'Always add the most specific ones first. '
                              'See the README for an example'),
                        required=False)
    args = parser.parse_args()
    # console.print(args.list)
    if args.list is None:
        introduction()
        login()
        # disabled for now
        # select_language()
        # task: Task = select_task()
        # if task is None:
        #     raise ValueError("Got no task")
        # We only have 1 task so don't bother about showing the menu
        task = tasks[0]
        ngrams: dict = task.labels.get_ngrams()
        # logger.debug(results)
        if ngrams is not None:
            print_ngram_table(ngrams)
            process_ngrams(ngrams)
        else:
            raise ValueError("results was None")
    else:
        task: Task = select_task()
        if task is None:
            raise ValueError("Got no task")
        process_user_supplied_qids(args=args, task=task)


if __name__ == "__main__":
    main()
