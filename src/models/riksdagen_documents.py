import logging

from wikibaseintegrator.wbi_helpers import execute_sparql_query

from src.helpers.console import console
from src.models.suggestion import Suggestion
from src.models.task import Task
from src.models.wikidata import Items, Item


class RiksdagenDocumentItems(Items):
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
        # Include spaces around the n-gram to avoid edits like this one
        # https://www.wikidata.org/w/index.php?title=Q40671507&diff=1497186802&oldid=1496945583
        # Lowercase is not needed here as Elastic matches anyway
        for search_string in suggestion.search_strings:
            results = execute_sparql_query(f'''
            SELECT DISTINCT ?item ?itemLabel 
            WHERE {{
              hint:Query hint:optimizer "None".
              SERVICE wikibase:mwapi {{
                bd:serviceParam wikibase:api "Search";
                                wikibase:endpoint "www.wikidata.org";
                                mwapi:srsearch 'haswbstatement:P8433 -haswbstatement:P921={suggestion.item.id} "{search_string}"' .
                ?title wikibase:apiOutput mwapi:title. 
              }}
              BIND(IRI(CONCAT(STR(wd:), ?title)) AS ?item)
              ?item rdfs:label ?label.
              # We lowercase the label first and search for the 
              # string in both the beginning, middle and end of the label
              FILTER(CONTAINS(LCASE(?label), " {search_string.lower()} "@{task.language_code.value}) || 
                     REGEX(LCASE(?label), ".* {search_string.lower()}$"@{task.language_code.value}) ||
                     REGEX(LCASE(?label), "^{search_string.lower()} .*"@{task.language_code.value}))
              # remove more specific forms of the main subject also
              # Thanks to Jan Ainali for this improvement :)
              MINUS {{?item wdt:P921 ?topic. ?topic wdt:P279 wd:{suggestion.item.id}. }}
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "sv". }}
            }}
            ''')
            for item_json in results["results"]["bindings"]:
                logging.debug(f"item_json:{item_json}")
                item = Item(json=item_json,
                            task=task)
                self.list.append(item)
            logging.info(f'Got {len(results["results"]["bindings"])} items from '
                         f'WDQS using the search string {search_string}')
        console.print(f"Got a total of {len(self.list)} items")
