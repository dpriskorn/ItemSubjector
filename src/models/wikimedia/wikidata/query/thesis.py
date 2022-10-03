from src.models.wikimedia.wikidata.query import Query


class ThesisQuery(Query):
    def __prepare_and_build_query__(self):
        self.query_string = (
            f"""
            SELECT DISTINCT ?item ?itemLabel
            WHERE {{
              {{
                ?item wdt:P31/wd:P279* wd:Q1266946. # thesis
              }} UNION
              {{
                ?item wdt:P31/wd:P279* wd:Q1385450. # dissertation
              }} UNION
              {{
                ?item wdt:P31/wd:P279* wd:Q3099732. # technical report
              }}
              MINUS {{
              ?item wdt:P921 wd:{self.main_subject_item.id};
              }}
              ?item rdfs:label ?label.
              FILTER(CONTAINS(LCASE(?label), " {self.search_string.lower()} "@{self.main_subject_item.task.language_code.value}) ||
                     REGEX(LCASE(?label), ".* {self.search_string.lower()}$"@{self.main_subject_item.task.language_code.value}) ||
                     REGEX(LCASE(?label), "^{self.search_string.lower()} .*"@{self.main_subject_item.task.language_code.value}))
              MINUS {{?item wdt:P921 ?topic. ?topic wdt:P279 wd:{self.main_subject_item.id}. }}
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}
            """
        )
