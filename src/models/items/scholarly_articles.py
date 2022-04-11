import logging

from wikibaseintegrator.wbi_helpers import execute_sparql_query  # type: ignore

import config
from src.helpers.cleaning import strip_bad_chars
from src.helpers.console import console
from src.models.items import Items
from src.models.suggestion import Suggestion
from src.models.task import Task
from src.models.wikimedia.wikidata.sparql_item import SparqlItem

logger = logging.getLogger(__name__)


class ScholarlyArticleItems(Items):
    """This supports both published peer reviewed articles and preprints"""

    def fetch_based_on_label(self, suggestion: Suggestion = None, task: Task = None):
        def build_query(
            suggestion: Suggestion = None,
            search_string: str = None,
            task: Task = None,
            cirrussearch_parameters: str = None,
        ):
            # TODO refactor
            if suggestion is None:
                raise ValueError("suggestion was None")
            if suggestion.item is None:
                raise ValueError("suggestion.item was None")
            if search_string is None:
                raise ValueError("search_string was None")
            if task is None:
                raise ValueError("task was None")
            if task.language_code is None:
                raise ValueError("task.language_code was None")
            if cirrussearch_parameters is None:
                raise ValueError("cirrussearch_parameters was None")
            # This query uses https://www.w3.org/TR/sparql11-property-paths/ to
            # find subjects that are subclass of one another up to 3 hops away
            # This query also uses the https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual/MWAPI
            # which has a hardcoded limit of 10,000 items so you will never get more matches than that
            # This query use regex to match beginning, middle and end of the label of matched items
            # The replacing lines should match the similar python replacements in cleaning.py
            # The replacing with "\\\\\\\\" becomes "\\\\" after leaving python and then it works in
            # SPARQL where it becomes "\\" and thus match a single backslash
            return f"""
                #{config.user_agent}
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
                """

        def process_results(results):
            # TODO refactor
            items = []
            for item_json in results["results"]["bindings"]:
                logging.debug(f"item_json:{item_json}")
                item = SparqlItem(**item_json)
                item.validate_qid_and_copy_label()
                if not item.is_in_blocklist():
                    items.append(item)
                else:
                    logger.info(f"{item.label} found in blocklist, skipping")
            return items

        if suggestion is None:
            raise ValueError("suggestion was None")
        if suggestion.item is None:
            raise ValueError("suggestion.item was None")
        if suggestion.args is None:
            raise ValueError("suggestion.args was None")
        if suggestion.args.limit_to_items_without_p921:
            raise Exception(
                "Limiting to items without P921 is not " "supported yet for this task."
            )
        if suggestion.search_strings is None:
            raise ValueError("suggestion.search_strings was None")
        if task is None:
            raise ValueError("task was None")
        if task.language_code is None:
            raise ValueError("task.language_code was None")
        if suggestion.args.limit_to_items_without_p921:
            console.print(
                "Limiting to scholarly articles without P921 main subject only"
            )
            cirrussearch_parameters = (
                f"haswbstatement:P31=Q13442814 -haswbstatement:P921"
            )
        else:
            cirrussearch_parameters = f"haswbstatement:P31=Q13442814 -haswbstatement:P921={suggestion.item.id}"
        # Fetch all items matching the search strings
        self.list = []
        for search_string in suggestion.search_strings:
            search_string = strip_bad_chars(search_string)
            results = execute_sparql_query(
                build_query(
                    cirrussearch_parameters=cirrussearch_parameters,
                    suggestion=suggestion,
                    search_string=search_string,
                    task=task,
                )
            )
            logging.info(
                f'Got {len(results["results"]["bindings"])} scholarly items from '
                f"WDQS using the search string {search_string}"
            )
            self.list.extend(process_results(results))
            # preprints
            # We don't use CirrusSearch in this query because we can do it more easily in
            # SPARQL on a small subgraph like this
            # find all items that are ?item wdt:P31/wd:P279* wd:Q1266946
            # minus the Qid we want to add
            results_preprint = execute_sparql_query(
                f"""
                #{config.user_agent}
                SELECT DISTINCT ?item ?itemLabel 
                WHERE {{
                  ?item wdt:P31/wd:P279* wd:Q580922. # preprint 
                  MINUS {{
                  ?item wdt:P921 wd:{suggestion.item.id};
                  }}
                  ?item rdfs:label ?label.
                  FILTER(CONTAINS(LCASE(?label), " {search_string.lower()} "@{task.language_code.value}) || 
                         REGEX(LCASE(?label), ".* {search_string.lower()}$"@{task.language_code.value}) ||
                         REGEX(LCASE(?label), "^{search_string.lower()} .*"@{task.language_code.value}))
                  MINUS {{?item wdt:P921/wdt:P279 wd:{suggestion.item.id}. }}
                  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
                }}
                """,
            )
            logging.info(
                f'Got {len(results["results"]["bindings"])} preprint items from '
                f"WDQS using the search string {search_string}"
            )
            self.list.extend(process_results(results_preprint))
        console.print(f"Got a total of {len(self.list)} items")
