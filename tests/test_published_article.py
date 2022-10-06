import argparse
from unittest import TestCase

from src import tasks
from src.models.wikimedia.wikidata.item.main_subject import MainSubjectItem
from src.models.wikimedia.wikidata.query.published_article import PublishedArticleQuery


class TestPublishedArticleQuery(TestCase):
    def test_published_article_query(self):
        msi = MainSubjectItem(
            id="Q407541",
            label="fentanyl",
            task=tasks[0],
            args=argparse.Namespace(
                no_aliases=dict(no_aliases=False),
                show_search_urls=dict(show_search_urls=False),
                limit_to_items_without_p921=dict(limit_to_items_without_p921=False),
            ),
        )
        msi.__extract_search_strings__()
        q = PublishedArticleQuery(main_subject_item=msi)
        for string in msi.search_strings:
            q.search_string = string
            q.__prepare_and_build_query__()
            print(q.query_string)
            assert (
                q.query_string.replace(" ", "").replace("\\", "").strip()
                == """
            #ItemSubjector (https://github.com/dpriskorn/ItemSubjector), User:So9q
            SELECT DISTINCT ?item ?itemLabel
            WHERE {
              hint:Query hint:optimizer "None".
              BIND(STR('haswbstatement:P31=Q13442814 -haswbstatement:P921 "fentanyl"') as ?search_string)
              SERVICE wikibase:mwapi {
                bd:serviceParam wikibase:api "Search";
                                wikibase:endpoint "www.wikidata.org";
                                mwapi:srsearch ?search_string.
                ?title wikibase:apiOutput mwapi:title.
              }
              BIND(IRI(CONCAT(STR(wd:), ?title)) AS ?item)
              ?item rdfs:label ?label.
              BIND(REPLACE(LCASE(?label), ",", "") as ?label1)
              BIND(REPLACE(?label1, ":", "") as ?label2)
              BIND(REPLACE(?label2, ";", "") as ?label3)
              BIND(REPLACE(?label3, "\\(", "") as ?label4)
              BIND(REPLACE(?label4, "\\)", "") as ?label5)
              BIND(REPLACE(?label5, "\\[", "") as ?label6)
              BIND(REPLACE(?label6, "\\]", "") as ?label7)
              BIND(REPLACE(?label7, "\\\\", "") as ?label8)
              BIND(?label8 as ?cleaned_label)
              FILTER(CONTAINS(?cleaned_label, ' fentanyl '@en) ||
                     REGEX(?cleaned_label, '.* fentanyl$'@en) ||
                     REGEX(?cleaned_label, '^fentanyl .*'@en))
              MINUS {?item wdt:P921/wdt:P279 wd:Q407541. }
              MINUS {?item wdt:P921/wdt:P279/wdt:P279 wd:Q407541. }
              MINUS {?item wdt:P921/wdt:P279/wdt:P279/wdt:P279 wd:Q407541. }
              SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }""".replace(
                    " ", ""
                )
                .replace("\\", "")
                .strip()
            )
            break
