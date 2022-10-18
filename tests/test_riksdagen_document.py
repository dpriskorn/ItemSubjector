import argparse
from unittest import TestCase

import config
from src import tasks
from src.models.wikimedia.wikidata.item.main_subject import MainSubjectItem
from src.models.wikimedia.wikidata.query.riksdagen_document import (
    RiksdagenDocumentQuery,
)


class TestRiksdagenDocumentQuery(TestCase):
    def test_riksdagen_document_query(self):
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
        q = RiksdagenDocumentQuery(main_subject_item=msi)
        for string in msi.search_strings:
            q.search_string = string
            config.username = "User:Username"
            q.__prepare_and_build_query__()
            print(q.query_string)
            assert (
                q.query_string.replace(" ", "").strip()
                == """
            #ItemSubjector (https://github.com/dpriskorn/ItemSubjector), User:So9q
            SELECT DISTINCT ?item ?itemLabel
            WHERE {
              hint:Query hint:optimizer "None".
              SERVICE wikibase:mwapi {
                bd:serviceParam wikibase:api "Search";
                                wikibase:endpoint "www.wikidata.org";
                                mwapi:srsearch 'haswbstatement:P8433 -haswbstatement:P921=Q407541 "fentanyl"' .
                ?title wikibase:apiOutput mwapi:title.
              }
              BIND(IRI(CONCAT(STR(wd:), ?title)) AS ?item)
              ?item rdfs:label ?label.
              # We lowercase the label first and search for the
              # string in both the beginning, middle and end of the label
              FILTER(CONTAINS(
                LCASE(?label), " fentanyl "@en) ||
                REGEX(LCASE(?label), ".* fentanyl$"@en) ||
                REGEX(LCASE(?label), "^fentanyl .*"@en)
              )
              # remove more specific forms of the main subject also
              # Thanks to Jan Ainali for this improvement :)
              MINUS {?main_subject_item wdt:P921 ?topic. ?topic wdt:P279 wd:Q407541. }
              SERVICE wikibase:label { bd:serviceParam wikibase:language "sv". }
            }""".replace(
                    " ", ""
                ).strip()
            )
            break
