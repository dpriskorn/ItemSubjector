# download all titles missing P921
import logging

from langdetect import detect, LangDetectException
from wikibaseintegrator import wbi_config
from wikibaseintegrator.wbi_helpers import execute_sparql_query

import config
from src import EntityID, console, Item

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

wbi_config.config['USER_AGENT'] = config.user_agent
results = execute_sparql_query("""
SELECT ?item ?title ?langcode
WHERE 
{{
  ?item wdt:P31 wd:Q5633421;
        wdt:P1476 ?title;
        wdt:P407 ?language.
  ?language wdt:P424 ?langcode.
  minus{{
  ?item wdt:P921 [].
  }}
  filter(lang(?title) = ?langcode)
}}
limit 10000
""")
ignore_list = ["ca", "ro", "no"]
if results is not None:
    count = 0
    red_count = 0
    total = len(results["results"]["bindings"])
    for result in results["results"]["bindings"]:
        item = Item(json=result)
        title = result["title"]["value"]
        title_language = result["title"]["xml:lang"]
        work_language = result["langcode"]["value"]
        # try:
        #     detected_language = detect(title)
        # except LangDetectException:
        #     logger.error(f"Could not detect language for {title}")
        #     detected_language = None
        # if len(title.split(" ")) < 4:
        #     short_title = True
        # else:
        #     short_title = False
        # if title_language != detected_language and short_title is False and detected_language not in ignore_list:
        #     console.print(f"[red]{item} {title} {title_language} {detected_language}[red]")
        #     red_count += 1
        # else:
        #     pass
        
        console.print(f"[green]{item.url()} {title} {title_language}[green]")
        #exit(0)
        count += 1
        if count % 10 == 0:
            print(f"{count}/{total}")