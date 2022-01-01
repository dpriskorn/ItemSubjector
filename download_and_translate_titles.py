# download all titles missing P921
import logging

from langdetect import detect, LangDetectException
from wikibaseintegrator import wbi_config
from wikibaseintegrator.wbi_helpers import execute_sparql_query

import config
from src import EntityID, console

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

wbi_config.config['USER_AGENT'] = config.user_agent
results = execute_sparql_query("""
SELECT ?item ?title
WHERE 
{{
  ?item wdt:P31 wd:Q5633421;
        wdt:P1476 ?title.
  minus{{
  ?item wdt:P921 [].
  }}
  filter(!(lang(?title) = "mul"))
  filter(!(lang(?title) = "und"))
}}
""")
ignore_list = ["ca", "ro", "no"]
if results is not None:
    count = 0
    red_count = 0
    total = len(results["results"]["bindings"])
    for result in results["results"]["bindings"]:
        item = str(EntityID(result["item"]["value"]))
        title = result["title"]["value"]
        language = result["title"]["xml:lang"]
        try:
            detected_language = detect(title)
        except LangDetectException:
            logger.error(f"Could not detect language for {title}")
            detected_language = None
        if len(title.split(" ")) < 4:
            short_title = True
        else:
            short_title = False
        if language != detected_language and short_title is False and detected_language not in ignore_list:
            console.print(f"[red]{item} {title} {language} {detected_language}[red]")
            red_count += 1
        else:
            pass
            # console.print(f"[green]{item} {title} {language} {detected_language}[green]")
        #exit(0)
        count += 1
        if count % 1000 == 0:
            logger.info(f"{count}/{red_count}/{total}")