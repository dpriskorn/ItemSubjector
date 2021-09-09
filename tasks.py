import logging

from wikibaseintegrator import wbi_config
from wikibaseintegrator.wbi_helpers import execute_sparql_query

import config
from helpers.console import console
from models.task import Task
from models.wikidata import Items, Item

#wbi_config.config['SPARQL_ENDPOINT_URL'] = config.endpoint

class ScholarlyArticles(Items):
    def fetch(self):
        """fetch_scientific_articles_without_main_subject"""
        logger = logging.getLogger(__name__)
        console.print("Fetching items")
        results = (execute_sparql_query(f'''
            #title:Scientific articles missing main subject
            #author:So9q inspired a query by Azertus
            #date:2021-09-09
            SELECT ?item ?itemLabel WHERE {{
                {{ SELECT * WHERE {{
                  SERVICE wikibase:mwapi {{
                    bd:serviceParam wikibase:endpoint "www.wikidata.org";
                                    wikibase:api "Search";
                                    mwapi:srsearch 'haswbstatement:P31=Q13442814';
                                    mwapi:language "en".
                    ?title wikibase:apiOutput mwapi:title. 
                  }}
                  BIND(URI(CONCAT('http://www.wikidata.org/entity/', ?title)) AS ?item)
                }} LIMIT 5 }}  
              MINUS {{
                ?item wdt:P921 [].  # main subject
              }}
              SERVICE wikibase:label {{
                bd:serviceParam wikibase:language "en" .
                ?item rdfs:label ?itemLabel .
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

tasks = [
    Task(
        label="Add main subject to scholarly articles",
        question="Is this a valid subject for this article?",
        items=scholarly_items
    )
]