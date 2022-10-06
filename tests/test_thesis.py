import argparse
from unittest import TestCase

from src import tasks
from src.models.wikimedia.wikidata.item.main_subject import MainSubjectItem
from src.models.wikimedia.wikidata.query.thesis import ThesisQuery


class TestThesisQuery(TestCase):
    def test_thesis_query(self):
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
        q = ThesisQuery(main_subject_item=msi)
        for string in msi.search_strings:
            q.search_string = string
            q.__prepare_and_build_query__()
            print(q.query_string)
            assert q.query_string.replace(" ","").strip() == """
            #ItemSubjector (https://github.com/dpriskorn/ItemSubjector), User:So9q
            SELECT DISTINCT ?item ?itemLabel
            WHERE {
              {
                ?item wdt:P31/wd:P279* wd:Q1266946. # thesis
              } UNION
              {
                ?item wdt:P31/wd:P279* wd:Q1385450. # dissertation
              } UNION
              {
                ?item wdt:P31/wd:P279* wd:Q3099732. # technical report
              }
              MINUS {
              ?item wdt:P921 wd:Q407541;
              }
              ?item rdfs:label ?label.
              FILTER(CONTAINS(LCASE(?label), " fentanyl "@en) ||
                     REGEX(LCASE(?label), ".* fentanyl$"@en) ||
                     REGEX(LCASE(?label), "^fentanyl .*"@en))
              MINUS {?item wdt:P921 ?topic. ?topic wdt:P279 wd:Q407541. }
              SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
            }""".replace(" ","").strip()
            break