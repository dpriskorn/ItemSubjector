from rich.console import Console

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
        "semi-automatically and validate the items found by searching Wikidata.\n"
        "E.g. the 2-gram 'breast cancer' corresponds to the item: Q128581: "
        "Breast cancer: cancer that originates in the mammary gland.\n"
        "The tool makes it simple to add main subject to a lot of items "
        "(in the example above there are ~8000 matches).\n"
        "Press Enter to start."
    )
