import config
from src import console
from src.models.wikimedia.wikidata.query.article import ArticleQuery


class PublishedArticleQuery(ArticleQuery):
    cirrussearch_parameters: str = ""

    def check_we_got_everything_we_need(self):
        if not self.main_subject_item:
            raise ValueError("suggestion was None")
        if not self.main_subject_item:
            raise ValueError("suggestion.main_subject_item was None")
        if not self.main_subject_item.args:
            raise ValueError("suggestion.args was None")
        if self.main_subject_item.args.limit_to_items_without_p921:
            raise Exception(
                "Limiting to items without P921 is not " "supported yet for this task."
            )
        if self.main_subject_item.task is None:
            raise ValueError("task was None")
        if self.main_subject_item.task.language_code is None:
            raise ValueError("task.language_code was None")
        if self.main_subject_item.args.limit_to_items_without_p921:
            console.print(
                "Limiting to scholarly articles without P921 main subject only"
            )
            cirrussearch_parameters = (
                f"haswbstatement:P31=Q13442814 -haswbstatement:P921"
            )
        else:
            cirrussearch_parameters = f"haswbstatement:P31=Q13442814 -haswbstatement:P921={self.main_subject_item.id}"
        if self.main_subject_item.task is None:
            raise ValueError("task was None")
        if self.main_subject_item.task.language_code is None:
            raise ValueError("task.language_code was None")
        if cirrussearch_parameters is None:
            raise ValueError("cirrussearch_parameters was None")

    def build_query(
        self,
    ):
        # This query uses https://www.w3.org/TR/sparql11-property-paths/ to
        # find subjects that are subclass of one another up to 3 hops away
        # This query also uses the https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual/MWAPI
        # which has a hardcoded limit of 10,000 items so you will never get more matches than that
        # This query use regex to match beginning, middle and end of the label of matched items
        # The replacing lines should match the similar python replacements in cleaning.py
        # The replacing with "\\\\\\\\" becomes "\\\\" after leaving python and then it works in
        # SPARQL where it becomes "\\" and thus match a single backslash
        self.query_string = f"""
            #{config.user_agent}
            SELECT DISTINCT ?item ?itemLabel
            WHERE {{
              hint:Query hint:optimizer "None".
              BIND(STR('{self.cirrussearch_parameters} \"{self.search_string}\"') as ?search_string)
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
              FILTER(CONTAINS(?cleaned_label, ' {self.search_string.lower()} '@{self.main_subject_item.task.language_code.value}) ||
                     REGEX(?cleaned_label, '.* {self.search_string.lower()}$'@{self.main_subject_item.task.language_code.value}) ||
                     REGEX(?cleaned_label, '^{self.search_string.lower()} .*'@{self.main_subject_item.task.language_code.value}))
              MINUS {{?item wdt:P921/wdt:P279 wd:{self.main_subject_item.id}. }}
              MINUS {{?item wdt:P921/wdt:P279/wdt:P279 wd:{self.main_subject_item.id}. }}
              MINUS {{?item wdt:P921/wdt:P279/wdt:P279/wdt:P279 wd:{self.main_subject_item.id}. }}
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}
            """
