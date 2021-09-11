import logging
from typing import List

from helpers.console import console
from helpers.menus import select_task
from models.ngram import NGram
from models.suggestion import Suggestion
from models.task import Task

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


def main():
    logger = logging.getLogger(__name__)
    print("Starting")
    # for now only English
    # chose_language()
    task: Task = select_task()
    if task is None:
        raise ValueError("Got no task")
    results = task.labels.get_ngrams()
    console.print(results)
    suggestions = []
    for result in results:
        ngram = NGram(
            label=result,
            frequency=results[result]
        )
        suggestion = ngram.recognize_named_entity()
        if suggestion is not None:
            suggestions.append(suggestion)
    for suggestion in suggestions:
        answer = console.input(f"Is this a valid main subject?\n"
                               f"{str(suggestion)}")
        if answer:
            console.print(f"Fetching items with labels that have {suggestion.ngram.label}")
            # items = Items()
            # items.fetch(query=suggestion.ngram.label)
            # show the user
            print("not implemented yet")


if __name__ == "__main__":
    main()