import logging

from wikibaseintegrator.wbi_helpers import execute_sparql_query

from helpers.cleaning import strip_bad_chars
from helpers.console import console
from models.suggestion import Suggestion
from models.task import Task
from models.wikidata import Items, Item


def build_query(suggestion: Suggestion = None,
                search_string: str = None,
                task: Task = None,
                cirrussearch_parameters: str = None):
    if suggestion is None:
        raise ValueError("suggestion was None")
    if search_string is None:
        raise ValueError("search_string was None")
    if task is None:
        raise ValueError("task was None")
    if cirrussearch_parameters is None:
        raise ValueError("cirrussearch_parameters was None")
    return (f"""
        SELECT DISTINCT ?item ?itemLabel 
        WHERE {{
          hint:Query hint:optimizer "None".
          BIND(STR('{cirrussearch_parameters} \"{search_string}\"') as ?search_string)
          SERVICE wikibase:mwapi {{
            bd:serviceParam wikibase:api "Search";
                            wikibase:endpoint "www.wikidata.org";
                            mwapi:srsearch ?search_string.
            ?title wikibase:apiOutput mwapi:title. 
          }}
          BIND(IRI(CONCAT(STR(wd:), ?title)) AS ?item)
          ?item rdfs:label ?label.
          BIND(REPLACE(LCASE(?label), ",", "") as ?label1)
          BIND(REPLACE(?label1, ":", "") as ?label2)
          BIND(REPLACE(?label2, ";", "") as ?label3)          
          BIND(REPLACE(?label3, "\\\\(", "") as ?label4)
          BIND(REPLACE(?label4, "\\\\)", "") as ?label5)
          BIND(REPLACE(?label5, "\\\\[", "") as ?label6)
          BIND(REPLACE(?label6, "\\\\]", "") as ?label7)
          BIND(REPLACE(?label7, "\\\\\\\\", "") as ?label8)
          BIND(?label8 as ?cleaned_label)
          FILTER(CONTAINS(?cleaned_label, ' {search_string.lower()} '@{task.language_code.value}) || 
                 REGEX(?cleaned_label, '.* {search_string.lower()}$'@{task.language_code.value}) ||
                 REGEX(?cleaned_label, '^{search_string.lower()} .*'@{task.language_code.value}))
          MINUS {{?item wdt:P921/wdt:P279 wd:{suggestion.item.id}. }}
          MINUS {{?item wdt:P921/wdt:P279/wdt:P279 wd:{suggestion.item.id}. }}
          MINUS {{?item wdt:P921/wdt:P279/wdt:P279/wdt:P279 wd:{suggestion.item.id}. }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """)


class ScholarlyArticleItems(Items):
    def fetch_based_on_label(self,
                             suggestion: Suggestion = None,
                             task: Task = None):
        # logger = logging.getLogger(__name__)
        if suggestion is None:
            raise ValueError("suggestion was None")
        if task is None:
            raise ValueError("task was None")
        if suggestion.args.limit_to_items_without_p921:
            console.print("Limiting to scholarly articles without P921 main subject only")
            cirrussearch_parameters = f"haswbstatement:P31=Q13442814 -haswbstatement:P921"
        else:
            cirrussearch_parameters = f"haswbstatement:P31=Q13442814 -haswbstatement:P921={suggestion.item.id}"
        # Fetch all items matching the search strings
        self.list = []
        for search_string in suggestion.search_strings:
            search_string = strip_bad_chars(search_string)
            # This query uses https://www.w3.org/TR/sparql11-property-paths/ to
            # find subjects that are subclass of one another up to 3 hops away
            # This query also uses the https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual/MWAPI
            # which has a hardcoded limit of 10,000 items so you will never get more matches than that
            # This query use regex to match beginning, middle and end of the label of matched items
            # The replacing lines should match the similar python replacements in cleaning.py
            # The replacing with "\\\\\\\\" becomes "\\\\" after leaving python and then it works in
            # SPARQL where it becomes "\\" and thus match a single backslash
            results = execute_sparql_query(
                build_query(
                    cirrussearch_parameters=cirrussearch_parameters,
                    suggestion=suggestion,
                    search_string=search_string,
                    task=task)
            )
            for item_json in results["results"]["bindings"]:
                logging.debug(f"item_json:{item_json}")
                item = Item(json=item_json)
                self.list.append(item)
            logging.info(f'Got {len(results["results"]["bindings"])} items from '
                         f'WDQS using the search string {search_string}')
        console.print(f"Got a total of {len(self.list)} items")
