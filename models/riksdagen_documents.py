import logging

from wikibaseintegrator.wbi_helpers import execute_sparql_query

from helpers.console import console
from models.suggestion import Suggestion
from models.task import Task
from models.wikidata import Labels, Items, Item


class RiksdagenDocumentLabels(Labels):
    """This class has all code needed to fetch Riksdagen documents, extract the labels,
    clean them and find the top n-grams we need"""

    # def get_ngrams(self) -> dict:
    #     # calculate_random_offset()
    #     # console.print(f"Calculated offset is: {config.random_offset} and will be used to randomize "
    #     #               f"the selection of scientific articles that are fetched")
    #     self.fetch_labels_into_dataframe(quantity=5000,
    #                                      # Fetch Riksdagen documents without main subject
    #                                      query="haswbstatement:P8433 -haswbstatement:P921")
    #     return self.extract_most_frequent_ngrams(quantity=7)


class RiksdagenDocumentItems(Items):
    def fetch_based_on_label(self,
                             suggestion: Suggestion = None,
                             task: Task = None):
        logger = logging.getLogger(__name__)
        if suggestion is None:
            raise ValueError("suggestion was None")
        if task is None:
            raise ValueError("task was None")
        # Fetch all items maching the search strings
        self.list = []
        for search_string in suggestion.search_strings:
            results = execute_sparql_query(f'''
            SELECT DISTINCT ?item ?itemLabel 
            WHERE {{
              hint:Query hint:optimizer "None".
              SERVICE wikibase:mwapi {{
                bd:serviceParam wikibase:api "Search";
                                wikibase:endpoint "www.wikidata.org";
                                # Include spaces around the n-gram to avoid edits like this one
                                # https://www.wikidata.org/w/index.php?title=Q40671507&diff=1497186802&oldid=1496945583
                                # Lowercase is not needed here as Elastic matches anyway
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
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
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
