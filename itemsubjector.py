import logging

from wikibaseintegrator import wbi_login, wbi_config
from wikibaseintegrator.datatypes import Item

import config
from helpers.console import console, ask_yes_no_question, introduction, print_ngram_table
from models.ngram import NGram
from models.scholarly_articles import ScholarlyArticleItems
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

# def process_entities(json_data):
#     #exit(0)
#     suggestions: List[Suggestion] = []
#     for annotation in json_data["annotations"]:
#         # we select first tag only for now
#         tag = annotation["tags"][0]
#         suggestion = Suggestion(
#             id=tag["id"],
#             # Pick the first label
#             label=tag["label"][0],
#             description=tag["desc"]
#         )
#         console.print(suggestion)
#         suggestions.append(suggestion)
#         # qid = tag["id"]
#         # label = tag["label"]
#         # description = tag["desc"]
#         # console.print(f"tag:{tag}\n"
#         #               f"label:{label}\n"
#         #               f"desc:{description}\n"
#         #               f"{config.wd_prefix+qid}\n")
#     return suggestions
#     # give the user a list to choose from
#     # when the user has chosen something, find other
#     # scientific articles with this entity label (using elastic search?)
#     # and that does not have this entity as main subject already
#     # and upload to all


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
            with console.status(f"Fetching items with labels that have '{suggestion.ngram.label}'..."):
                items = ScholarlyArticleItems()
                items.fetch_based_on_label(suggestion=suggestion)
            console.print(f"Got len(items.list) items from WDQS")
            for item in items.list:
                with console.status(f"Uploading main subject {suggestion.ngram.label} to {item.label}"):
                    # NOTE when upgrading to v0.12 change ItemID -> Item
                    reference = Item(
                            "Q69652283",  # inferred from title
                            prop_nr="P887"  # based on heuristic
                        )
                    statement = Item(
                            suggestion.id,
                            prop_nr="P921",  # main subject
                            references=[reference]
                        )
                    item.upload_one_statement_to_wikidata(
                        statement=statement,
                        summary=f"{suggestion.id}: {suggestion.label}"
                    )
                console.print(item.url())
                exit(0)
            raise Exception("exit here now")
        else:
            console.print("Skipping this suggestion")
        console.print("\n")


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

if __name__ == "__main__":
    main()