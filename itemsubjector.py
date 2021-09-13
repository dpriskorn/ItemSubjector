import argparse
import logging

from wikibaseintegrator import wbi_login, wbi_config
from wikibaseintegrator.datatypes import Item as ItemType
from wikibaseintegrator.wbi_enums import ActionIfExists

import config
from helpers.console import console, ask_yes_no_question, introduction, print_ngram_table, \
    print_best_practice_information
from models.ngram import NGram
from models.scholarly_articles import ScholarlyArticleItems
from models.suggestion import Suggestion
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


def add_suggestion_to_items(suggestion: Suggestion = None):
    if suggestion is None:
        raise ValueError("Suggestion was None")
    with console.status(f"Fetching items with labels that have '{suggestion.ngram.label}'..."):
        items = ScholarlyArticleItems()
        items.fetch_based_on_label(suggestion=suggestion)
    console.print(f"Got {len(items.list)} items from WDQS")
    for item in items.list:
        with console.status(f"Uploading main subject {suggestion.ngram.label} to {item.label}"):
            main_subject_property = "P921"
            reference = ItemType(
                "Q69652283",  # inferred from title
                prop_nr="P887"  # based on heuristic
            )
            statement = ItemType(
                suggestion.id,
                prop_nr=main_subject_property,
                references=[reference]
            )
            item.upload_one_statement_to_wikidata(
                statement=statement,
                summary=f"[[Property:{main_subject_property}]]: [[{suggestion.id}]]"
            )
        console.print(f"Added {suggestion.label} to {item.label}: {item.url()}")


def process_results(results):
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


def process_user_supplied_qids(args):
    print_best_practice_information()
    for qid in args.list:
        item = Item(
            id=qid
        )
        console.print(f"Working on {item}")
        # generate suggestion
        suggestion = Suggestion(
            id=item.id,
            label=item.label,
            ngram=NGram(
                label=item.label,
                frequency=None
            )
        )
        add_suggestion_to_items(suggestion=suggestion)


def login():
    with console.status("Logging in with WikibaseIntegrator..."):
        if config.legacy_wbi:
            config.login_instance = wbi_login.Login(
                user=config.username, pwd=config.password
            )
            # Set User-Agent
            wbi_config.config["USER_AGENT_DEFAULT"] = config.user_agent
        else:
            config.login_instance = wbi_login.Login(
                auth_method='login',
                user=config.username,
                password=config.password,
                debug=False
            )
            # Set User-Agent
            wbi_config.config["USER_AGENT_DEFAULT"] = config.user_agent


def main():
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list',
                        nargs='+',
                        help=('List of QIDs that are to be added as '
                              'main subjects on scientific articles. '
                              'Always add the most specific ones first. '
                              'See the README for an example'),
                        required=False)
    args = parser.parse_args()
    console.print(args.list)
    if args.list is None:
        introduction()
        login()
        # for now only English
        # chose_language()
        # task: Task = select_task()
        # if task is None:
        #     raise ValueError("Got no task")
        # We only have 1 task so don't bother about showing the menu
        task = tasks[0]
        results = task.labels.get_ngrams()
        logger.debug(results)
        if results is not None:
            print_ngram_table(results)
            process_results(results)
        else:
            raise ValueError("results was None")
    else:
        login()
        process_user_supplied_qids(args)


if __name__ == "__main__":
    main()