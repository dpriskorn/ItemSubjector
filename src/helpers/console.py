from rich.console import Console

console = Console()


def print_keep_an_eye_on_wdqs_lag():
    console.print(
        "Please keep an eye on the lag of the WDQS cluster here and avoid "
        "working if it is over a few minutes.\n"
        "https://grafana.wikimedia.org/d/000000489/wikidata-query-service?"
        "orgId=1&viewPanel=8&from=now-30m&to=now&refresh=1d "
        "You can see if any lagging servers are pooled here\n"
        "https://config-master.wikimedia.org/pybal/eqiad/wdqs\n"
        "If any enabled servers are lagging more than 5-10 minutes "
        "you can search phabricator for open tickets to see if the team is on it.\n"
        "If you don't find any feel free to create a new ticket like this:\n"
        "https://phabricator.wikimedia.org/T291621"
    )


def press_enter_to_continue():
    console.input("Press Enter to continue.")
