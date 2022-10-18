import argparse
from unittest import TestCase

import config
from src import tasks
from src.models.wikimedia.wikidata.item.main_subject import MainSubjectItem
from src.models.wikimedia.wikidata.query.preprint_article import PreprintArticleQuery


class TestPreprintArticle(TestCase):
    def test_preprint_article_query(self):
        msi = MainSubjectItem(
            id="Q407541",
            label="fentanyl",
            task=tasks[0],
            args=argparse.Namespace(
                no_aliases=dict(no_aliases=False),
                show_search_urls=dict(show_search_urls=False),
            ),
        )
        msi.__extract_search_strings__()
        q = PreprintArticleQuery(main_subject_item=msi)
        for string in msi.search_strings:
            q.search_string = string
            config.username = "User:Username"
            q.__prepare_and_build_query__()
            print(q.query_string)
            assert (
                q.query_string.replace(" ", "").strip()
                == """
            #ItemSubjector (https://github.com/dpriskorn/ItemSubjector), User:Username
            SELECT DISTINCT ?item ?itemLabel
            WHERE {
              ?item wdt:P31/wd:P279* wd:Q580922. # preprint
              MINUS {
              ?item wdt:P921 wd:Q407541;
              }
              ?item rdfs:label ?label.
              FILTER(CONTAINS(
                LCASE(?label), " fentanyl "
                     @en) ||
                REGEX(LCASE(?label), ".* fentanyl$"
                     @en) ||
                REGEX(LCASE(?label), "^fentanyl .*"
                     @en)
              )
              MINUS {?item wdt:P921/wdt:P279 wd:Q407541. }
              SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }""".replace(
                    " ", ""
                ).strip()
            )
            break
