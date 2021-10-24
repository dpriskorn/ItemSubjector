import logging

from wikibaseintegrator.wbi_helpers import execute_sparql_query

from src.helpers.cleaning import strip_bad_chars
from src.helpers.console import console
from src.models.suggestion import Suggestion
from src.models.task import Task
from src.models.wikidata import Items, Item


def process_results(results):
    items = []
    for item_json in results["results"]["bindings"]:
        logging.debug(f"item_json:{item_json}")
        item = Item(json=item_json)
        items.append(item)
    return items


class AcademicJournalItems(Items):
    """This supports both published peer reviewed articles and preprints"""

    def fetch_based_on_label(self,
                             suggestion: Suggestion = None,
                             task: Task = None):
        # logger = logging.getLogger(__name__)
        if suggestion is None:
            raise ValueError("suggestion was None")
        if task is None:
            raise ValueError("task was None")
        # Fetch all items matching the search strings
        self.list = []
        for search_string in suggestion.search_strings:
            search_string = strip_bad_chars(search_string)
            results = execute_sparql_query(f"""
            SELECT ?item ?itemLabel
            WHERE 
            {{
              ?item wdt:P31 wd:Q737498.
              minus {{?item wdt:P921 wd:{suggestion.item.id}.}}
              ?item rdfs:label ?label.
              # We lowercase the label first and search for the 
              # string in both the beginning, middle and end of the label
              FILTER(CONTAINS(LCASE(?label), " {search_string.lower()} "@{task.language_code.value}) || 
                     REGEX(LCASE(?label), ".* {search_string.lower()}$"@{task.language_code.value}) ||
                     REGEX(LCASE(?label), "^{search_string.lower()} .*"@{task.language_code.value}))
              MINUS {{?item wdt:P921/wdt:P279 wd:{suggestion.item.id}. }}
              MINUS {{?item wdt:P921/wdt:P279/wdt:P279 wd:{suggestion.item.id}. }}
              MINUS {{?item wdt:P921/wdt:P279/wdt:P279/wdt:P279 wd:{suggestion.item.id}. }}
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}
            """,
                                           debug=suggestion.args.debug_sparql)
            logging.info(f'Got {len(results["results"]["bindings"])} academic journal items from '
                         f'WDQS using the search string {search_string}')
            self.list.extend(process_results(results))
        console.print(f"Got a total of {len(self.list)} items")
