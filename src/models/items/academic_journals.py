# import logging
#
# from wikibaseintegrator.wbi_helpers import execute_sparql_query  # type: ignore
#
# import config
# from src.helpers.cleaning import __strip_bad_chars__
# from src.helpers.console import console
# from src.models.items import Items
# from src.models.suggestion import Suggestion
# from src.models.task import Task
# from src.models.wikimedia.wikidata.sparql_item import SparqlItem
#
#
# class AcademicJournalItems(Items):
#     """This supports both published peer reviewed articles and preprints"""
#
#     def fetch_based_on_label(self, suggestion: Suggestion = None, task: Task = None):
#         def process_results(results):
#             # TODO refactor into private method
#             items = []
#             for item_json in results["results"]["bindings"]:
#                 logging.debug(f"item_json:{item_json}")
#                 item = SparqlItem(**item_json)
#                 items.append(item)
#             return items
#
#         # logger = logging.getLogger(__name__)
#         if suggestion is None:
#             raise ValueError("suggestion was None")
#         if task is None:
#             raise ValueError("task was None")
#         if task.language_code is None:
#             raise ValueError("task.language_code was None")
#         if suggestion.search_strings is None:
#             raise ValueError("suggestion.search_strings was None")
#         if suggestion.main_subject_item is None:
#             raise ValueError("suggestion.main_subject_item was None")
#         if suggestion.main_subject_item.id is None:
#             raise ValueError("suggestion.main_subject_item.id was None")
#         if suggestion.args is None:
#             raise ValueError("suggestion.args was None")
#         # Fetch all items matching the search strings
#         self.list = []
#         for search_string in suggestion.search_strings:
#             search_string = __strip_bad_chars__(search_string)
#             results = execute_sparql_query(
#                 f"""
#             #{config.user_agent}
#             SELECT ?main_subject_item ?itemLabel
#             WHERE
#             {{
#               ?main_subject_item wdt:P31 wd:Q737498.
#               minus {{?main_subject_item wdt:P921 wd:{suggestion.main_subject_item.id}.}}
#               ?main_subject_item rdfs:label ?label.
#               # We lowercase the label first and search for the
#               # string in both the beginning, middle and end of the label
#               FILTER(CONTAINS(LCASE(?label), " {search_string.lower()} "@{task.language_code.value}) ||
#                      REGEX(LCASE(?label), ".* {search_string.lower()}$"@{task.language_code.value}) ||
#                      REGEX(LCASE(?label), "^{search_string.lower()} .*"@{task.language_code.value}))
#               MINUS {{?main_subject_item wdt:P921/wdt:P279 wd:{suggestion.main_subject_item.id}. }}
#               MINUS {{?main_subject_item wdt:P921/wdt:P279/wdt:P279 wd:{suggestion.main_subject_item.id}. }}
#               MINUS {{?main_subject_item wdt:P921/wdt:P279/wdt:P279/wdt:P279 wd:{suggestion.main_subject_item.id}. }}
#               SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
#             }}
#             """,
#             )
#             logging.info(
#                 f'Got {len(results["results"]["bindings"])} academic journal items from '
#                 f"WDQS using the search string {search_string}"
#             )
#             self.list.extend(process_results(results))
#         console.print(f"Got a total of {len(self.list)} items")
