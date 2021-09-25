import logging

from wikibaseintegrator.wbi_helpers import execute_sparql_query

from helpers.cleaning import strip_bad_chars
from helpers.console import console
from models.suggestion import Suggestion
from models.task import Task
from models.wikidata import Items, Item


class ScholarlyArticleItems(Items):
    def fetch_based_on_label(self,
                             suggestion: Suggestion = None,
                             task: Task = None):
        # logger = logging.getLogger(__name__)
        if suggestion is None:
            raise ValueError("suggestion was None")
        if task is None:
            raise ValueError("task was None")
        # Fetch all items maching the search strings
        self.list = []
        for search_string in suggestion.search_strings:
            search_string = strip_bad_chars(search_string)
            results = execute_sparql_query(f"""
            SELECT DISTINCT ?item ?itemLabel 
            WHERE {{
              hint:Query hint:optimizer "None".
              BIND(STR('haswbstatement:P31=Q13442814 -haswbstatement:P921={suggestion.item.id} \"{search_string}\"') as ?search_string)
              SERVICE wikibase:mwapi {{
                bd:serviceParam wikibase:api "Search";
                                wikibase:endpoint "www.wikidata.org";
                                mwapi:srsearch ?search_string.
                ?title wikibase:apiOutput mwapi:title. 
              }}
              BIND(IRI(CONCAT(STR(wd:), ?title)) AS ?item)
              ?item rdfs:label ?label.
              # This has to match the function in cleaning.py
              BIND(REPLACE(LCASE(?label), ",", "") as ?label1)
              BIND(REPLACE(?label1, ":", "") as ?label2)
              BIND(REPLACE(?label2, ";", "") as ?label3)          
              BIND(REPLACE(?label3, "\\\\(", "") as ?label4)
              BIND(REPLACE(?label4, "\\\\)", "") as ?label5)
              BIND(REPLACE(?label5, "\\\\[", "") as ?label6)
              BIND(REPLACE(?label6, "\\\\]", "") as ?label7)
              # This results in //->/ after leaving python
              BIND(REPLACE(?label7, "\\\\\\\\", "") as ?label8)
              BIND(?label8 as ?cleaned_label)
              # We try matching beginning, middle and end
              FILTER(CONTAINS(?cleaned_label, ' {search_string.lower()} '@{task.language_code.value}) || 
                     REGEX(?cleaned_label, '.* {search_string.lower()}$'@{task.language_code.value}) ||
                     REGEX(?cleaned_label, '^{search_string.lower()} .*'@{task.language_code.value}))
              # remove more specific forms of the main subject also
              MINUS {{?item wdt:P921 ?topic. ?topic wdt:P279 wd:{suggestion.item.id}. }}
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}
            """)
            for item_json in results["results"]["bindings"]:
                logging.debug(f"item_json:{item_json}")
                item = Item(json=item_json)
                self.list.append(item)
            logging.info(f'Got {len(results["results"]["bindings"])} items from '
                         f'WDQS using the search string {search_string}')
        console.print(f"Got a total of {len(self.list)} items")
