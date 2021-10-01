import logging

from wikibaseintegrator.wbi_helpers import execute_sparql_query

from src.helpers.console import console
from src.models.suggestion import Suggestion
from src.models.task import Task
from src.models.wikidata import Items, Item

# There were ~16.000 thesis' in WD when this was written


class ThesisItems(Items):
    def fetch_based_on_label(self,
                             suggestion: Suggestion = None,
                             task: Task = None):
        # logger = logging.getLogger(__name__)
        if suggestion is None:
            raise ValueError("suggestion was None")
        if suggestion.args.limit_to_items_without_p921:
            raise Exception("Limiting to items without P921 is not "
                            "supported yet for this task.")
        if task is None:
            raise ValueError("task was None")
        # Fetch all items maching the search strings
        self.list = []
        for search_string in suggestion.search_strings:
            # We don't use CirrusSearch in this query because we can do it more easily in
            # SPARQL on a small subgraph like this
            # find all items that are ?item wdt:P31/wd:P279* wd:Q1266946
            # minus the QID we want to add
            results = execute_sparql_query(f'''
            SELECT DISTINCT ?item ?itemLabel 
            WHERE {{
              {{
                ?item wdt:P31/wd:P279* wd:Q1266946. # thesis
              }} UNION
              {{
                ?item wdt:P31/wd:P279* wd:Q1385450. # dissertation
              }} UNION
              {{
                ?item wdt:P31/wd:P279* wd:Q3099732. # technical report
              }}
              MINUS {{
              ?item wdt:P921 wd:{suggestion.item.id};
              }}
              ?item rdfs:label ?label.
              FILTER(CONTAINS(LCASE(?label), " {search_string.lower()} "@{task.language_code.value}) || 
                     REGEX(LCASE(?label), ".* {search_string.lower()}$"@{task.language_code.value}) ||
                     REGEX(LCASE(?label), "^{search_string.lower()} .*"@{task.language_code.value}))
              MINUS {{?item wdt:P921 ?topic. ?topic wdt:P279 wd:{suggestion.item.id}. }}
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}
            ''', debug=suggestion.args.debug_sparql)
            for item_json in results["results"]["bindings"]:
                logging.debug(f"item_json:{item_json}")
                item = Item(json=item_json,
                            task=task)
                self.list.append(item)
            logging.info(f'Got {len(results["results"]["bindings"])} items from '
                         f'WDQS using the search string {search_string}')
        console.print(f"Got a total of {len(self.list)} items")
