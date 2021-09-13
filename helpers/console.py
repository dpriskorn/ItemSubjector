from rich.console import Console
from rich.table import Table

console = Console()


def ask_yes_no_question(message: str):
    # https://www.quora.com/
    # I%E2%80%99m-new-to-Python-how-can-I-write-a-yes-no-question
    # this will loop forever
    while True:
        answer = console.input(message + ' [Y/Enter/n]: ')
        if len(answer) == 0 or answer[0].lower() in ('y', 'n'):
            if len(answer) == 0:
                return True
            else:
                # the == operator just returns a boolean,
                return answer[0].lower() == 'y'


def introduction():
    console.input(
        "This tool enables you to find n-grams from labels "
        "semi-automatically and validate the match between the n-grams "
        "with items found by searching Wikidata.\n"
        "E.g. the 2-gram 'breast cancer' corresponds to the item: Q128581: "
        "Breast cancer: cancer that originates in the mammary gland.\n"
        "The tool makes it simple to add main subject to a lot of items "
        "(in the example above there are ~8000 matches).\n"
        "Note: If unsure you should reject a match when validating.\n"
        "Press Enter to start."
    )


def print_best_practice_information():
    console.input(
        "When adding QID main subjects please try to first "
        "educate yourself about the subarea of science a little "
        "and find/create items as specific as possible.\n"
        "E.g. when searching for 'cancer screening' in Wikidata "
        "we find 'gastric cancer screening' in labels of "
        "scientific articles but there is "
        "perhaps no item for this yet.\n"
        "In this case it is preferred to first create that item "
        "(done in Q108532542 and add that as main subject and "
        "avoid the more general 'cancer screening' until all "
        "subforms of screening are added.\n"
        "Press Enter to start."
    )


def print_ngram_table(results):
    table = Table(title="N-grams found")
    table.add_column("N-gram")
    table.add_column("Frequency")
    for ngram in results:
        table.add_row(ngram, str(results[ngram]))
    console.print(table)
