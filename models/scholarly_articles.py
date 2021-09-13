import logging

from wikibaseintegrator.wbi_helpers import execute_sparql_query

import config
from helpers.calculations import calculate_random_offset
from helpers.console import console
from models.suggestion import Suggestion
from models.wikidata import Labels, Items, Item


class ScholarlyArticleLabels(Labels):
    """This class has all code needed to fetch scientific articles, extract the labels,
    clean them and find the top n-grams we need"""

    def get_ngrams(self):
        # calculate_random_offset()
        # console.print(f"Calculated offset is: {config.random_offset} and will be used to randomize "
        #               f"the selection of scientific articles that are fetched")
        self.fetch_labels_into_dataframe(quantity=5000,
                                         # Fetch scientific articles without main subject
                                         query="haswbstatement:P31=Q13442814 -haswbstatement:P921")
        return self.extract_most_frequent_ngrams(quantity=7)


class ScholarlyArticleItems(Items):
    def fetch_based_on_label(self,
                             suggestion: Suggestion = None):
        logger = logging.getLogger(__name__)
        if suggestion is None:
            raise ValueError("suggestion was None")
        results = execute_sparql_query(f'''
            #title:Scientific articles without main subject and "breast cancer" in the label
            SELECT DISTINCT ?item ?itemLabel 
            WHERE {{
              hint:Query hint:optimizer "None".
              SERVICE wikibase:mwapi {{
                bd:serviceParam wikibase:api "Search";
                                wikibase:endpoint "www.wikidata.org";
                                # Include spaces around the n-gram to avoid edits like this one
                                # https://www.wikidata.org/w/index.php?title=Q40671507&diff=1497186802&oldid=1496945583
                                mwapi:srsearch 'haswbstatement:P31=Q13442814 -haswbstatement:P921={suggestion.id} " {suggestion.ngram.label} "' .
                ?title wikibase:apiOutput mwapi:title. 
              }}
              BIND(IRI(CONCAT(STR(wd:), ?title)) AS ?item)
              ?item rdfs:label ?label.
              filter(contains(?label, "{suggestion.ngram.label}"@en))
              # remove more specific forms of the main subject also
              # Thanks to Jan Ainali for this improvement :)
              MINUS {{?item wdt:P921 ?topic. ?topic wdt:P279 wd:{suggestion.id}. }}
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}
        ''')
        self.list = []
        for item_json in results["results"]["bindings"]:
            logging.debug(f"item_json:{item_json}")
            item = Item(json=item_json)
            self.list.append(item)
        logging.info(f"Got {len(self.list)} items from "
                     f"WDQS")
