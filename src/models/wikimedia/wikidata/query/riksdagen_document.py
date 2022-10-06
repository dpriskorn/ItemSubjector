import config
from src.models.wikimedia.wikidata.query import Query


class RiksdagenDocumentQuery(Query):
    def __prepare_and_build_query__(self):
        lang = self.main_subject_item.task.language_code.value
        self.query_string = f"""
            #{config.user_agent}
            SELECT DISTINCT ?item ?itemLabel
            WHERE {{
              hint:Query hint:optimizer "None".
              SERVICE wikibase:mwapi {{
                bd:serviceParam wikibase:api "Search";
                                wikibase:endpoint "www.wikidata.org";
                                mwapi:srsearch 'haswbstatement:P8433 -haswbstatement:P921={self.main_subject_item.id} "{self.search_string}"' .
                ?title wikibase:apiOutput mwapi:title.
              }}
              BIND(IRI(CONCAT(STR(wd:), ?title)) AS ?item)
              ?item rdfs:label ?label.
              # We lowercase the label first and search for the
              # string in both the beginning, middle and end of the label
              FILTER(CONTAINS(
                LCASE(?label), " {self.search_string.lower()} "@{lang}) ||
                REGEX(LCASE(?label), ".* {self.search_string.lower()}$"@{lang}) ||
                REGEX(LCASE(?label), "^{self.search_string.lower()} .*"@{lang})
              )
              # remove more specific forms of the main subject also
              # Thanks to Jan Ainali for this improvement :)
              MINUS {{?main_subject_item wdt:P921 ?topic. ?topic wdt:P279 wd:{self.main_subject_item.id}. }}
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "sv". }}
            }}
            """
