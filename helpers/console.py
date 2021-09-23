from typing import List, Dict

from rich.console import Console
from rich.table import Table

from models.wikidata import Items

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
    print_keep_an_eye_on_wdqs_lag()
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


def print_keep_an_eye_on_wdqs_lag():
    console.print("Please keep an eye on the lag of the WDQS cluster here and avoid "
                  "working if it is over a few minutes.\n"
                  "https://grafana.wikimedia.org/d/000000489/wikidata-query-service?"
                  "orgId=1&viewPanel=8&from=now-30m&to=now&refresh=1d "
                  "You can see if any lagging servers are pooled here\n"
                  "https://config-master.wikimedia.org/pybal/eqiad/wdqs\n"
                  "If any enabled servers are lagging more than 5-10 minutes "
                  "you can search phabricator for open tickets to see if the team is on it.\n"
                  "If you don't find any feel free to create a new ticket like this:\n"
                  "https://phabricator.wikimedia.org/T291621")


def press_enter_to_start():
    console.input("Press Enter to start.")


def print_scholarly_articles_best_practice_information():
    print_keep_an_eye_on_wdqs_lag()
    console.print(
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
        "subforms of screening are added."
    )
    press_enter_to_start()


def print_riksdagen_documents_best_practice_information():
    print_keep_an_eye_on_wdqs_lag()
    press_enter_to_start()


def print_ngram_table(results: Dict):
    table = Table(title="N-grams found")
    table.add_column("N-gram")
    table.add_column("Frequency")
    for ngram in results:
        table.add_row(ngram, str(results[ngram]))
    console.print(table)


def print_search_strings_table(search_strings: List[str]):
    table = Table(title="Search strings")
    table.add_column(f"Extracted the following {len(search_strings)} search strings:")
    for string in search_strings:
        table.add_row(string)
    console.print(table)


def print_found_items_table(items: Items = None):
    if items is None:
        raise ValueError("items was None")
    table = Table(title="Matched items found")
    table.add_column("Showing only the first 50 items if more are found")
    for item in items.list[0:50]:
        table.add_row(item.label)
    console.print(table)


def ask_add_to_job_queue(items: Items = None):
    return ask_yes_no_question(f"Do you want to add this job with {len(items.list)} items to the queue?")


def print_running_jobs(jobs):
    console.print(f"Running {len(jobs)} job(s) "
                  f"non-interactively now. You can take a "
                  f" coffee break and lean back :)")


def print_finished():
    console.print("All jobs finished successfully")
