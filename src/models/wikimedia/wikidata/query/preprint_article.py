import config
from src.models.wikimedia.wikidata.query import Query


class PreprintArticleQuery(Query):
    def __prepare_and_build_query__(self):
        # We don't use CirrusSearch in this query because we can do it more easily in
        # SPARQL on a small subgraph like this
        # find all items that are ?main_subject_item wdt:P31/wd:P279* wd:Q1266946
        # minus the Qid we want to add
        self.query_string = f"""
        #{config.user_agent}
        SELECT DISTINCT ?item ?itemLabel
        WHERE {{
          ?item wdt:P31/wd:P279* wd:Q580922. # preprint
          MINUS {{
          ?item wdt:P921 wd:{self.main_subject_item.id};
          }}
          ?item rdfs:label ?label.
          FILTER(CONTAINS(
            LCASE(?label), " {self.search_string.lower()} "
                 @{self.main_subject_item.task.language_code.value}) ||
            REGEX(LCASE(?label), ".* {self.search_string.lower()}$"
                 @{self.main_subject_item.task.language_code.value}) ||
            REGEX(LCASE(?label), "^{self.search_string.lower()} .*"
                 @{self.main_subject_item.task.language_code.value})
          )
          MINUS {{?item wdt:P921/wdt:P279 wd:{self.main_subject_item.id}. }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """
