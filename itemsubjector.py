import logging

from wikibaseintegrator.datatypes import Item

from helpers.console import console, ask_yes_no_question, introduction
from helpers.menus import select_task
from models.ngram import NGram
from models.scholarly_articles import ScholarlyArticleItems
from models.task import Task
from models.wikidata import Statement
from tasks import tasks

logging.basicConfig(level=logging.DEBUG)

# pseudo code
# let user choose what to work on ie.
# let user choose language and subgraph
# e.g. Swedish documents from Riksdagen
# e.g. English scientific articles


# loop:
# get some labels
# do NER on a label
# let the user chose 1 meaningful match
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
    console.status("Searching the Wikidata API for entities matching the found n-grams...")
    for result in results:
        ngram = NGram(
            label=result,
            frequency=results[result]
        )
        suggestion = ngram.recognize_named_entity()
        if suggestion is not None:
            suggestions.append(suggestion)
    console.print("Found the following candidates:", "bold")
    for suggestion in suggestions:
        answer = ask_yes_no_question(f"{str(suggestion)}\n"
                                     f"Is this a valid main subject?")
        if answer:
            console.print(f"Fetching items with labels that have '{suggestion.ngram.label}'")
            items = ScholarlyArticleItems()
            items.fetch_based_on_label(suggestion=suggestion)
            console.print(items.list)
            for item in items.list:
                console.status(f"Uploading main subject {suggestion.ngram.label} to {item.label}")
                reference = Item(
                        "Q69652283", # inferred from title
                        prop_nr="P887"  # based on heuristic
                    )
                main_statement = Item(
                        suggestion.id,
                        prop_nr="P921"  # main subject
                    )
                statement = Statement(
                    statement=main_statement,
                    references=[reference]
                )
                item.upload_one_statement_to_wikidata(statement)
                console.print(item.url())
                exit(0)
            raise Exception("exit here now")
        else:
            console.print("Skipping this suggestion")
        console.print("\n")



def main():
    logger = logging.getLogger(__name__)
    introduction()
    # for now only English
    # chose_language()
    # task: Task = select_task()
    # if task is None:
    #     raise ValueError("Got no task")
    # We only have 1 task so don't bother about showing the menu
    task = tasks[0]
    results = task.labels.get_ngrams()
    console.print(results)
    if results is not None:
        process_results(results)
    else:
        raise ValueError("results was None")

if __name__ == "__main__":
    main()