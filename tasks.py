import logging

from wikibaseintegrator import wbi_config
from wikibaseintegrator.wbi_helpers import execute_sparql_query

import config
from models.task import Task
from models.wikidata import Items, Item

#wbi_config.config['SPARQL_ENDPOINT_URL'] = config.endpoint

class ScholarlyArticles(Items):
    def fetch_scientific_articles_without_main_subject(self):
        logger = logging.getLogger(__name__)
        results = (execute_sparql_query(f'''
            #title:Scientific articles missing main subject
            SELECT DISTINCT ?item ?itemLabel WHERE {{
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
              {{
                SELECT DISTINCT ?item WHERE {{
                  ?item p:P31 ?statement0;
                        rdfs:label ?label.
                  ?statement0 (ps:P31/(wdt:P279*)) wd:Q13442814.
                  minus{{
                    ?item wdt:P921 [].  # main subject
                    }}
                  filter(lang(?label) = "en").
                }}
                LIMIT 10
              }}
            }}
        ''', endpoint=config.endpoint))
        logger.info("Got the data")
        logger.debug(f"data:{results.keys()}")
        try:
            logger.debug(f"data:{results['results']['bindings']}")
            for entry in results["results"]['bindings']:
                logger.debug(f"data:{entry.keys()}")
                logging.debug(f"json:{entry}")
                item = Item(json=entry)
                self.list.append(item)
        except KeyError:
            logger.error("Got no results")
        logger.info(f"Got {len(self.list)} "
                    f"items from WDQS")

scholarly_items = ScholarlyArticles()
scholarly_items.fetch_scientific_articles_without_main_subject()

tasks = [
    Task(
        label="Add main subject to scholarly articles",
        question="Is this a valid subject for this article?",
        items=scholarly_items
    )
]