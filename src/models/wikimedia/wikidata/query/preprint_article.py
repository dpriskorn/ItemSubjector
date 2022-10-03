import config
from src.models.wikimedia.wikidata.query.article import ArticleQuery


class PreprintArticleQuery(ArticleQuery):
    def __build_query__(self):
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
