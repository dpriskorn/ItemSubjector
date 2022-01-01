# download all titles missing P921
from langdetect import detect
from wikibaseintegrator import wbi_config
from wikibaseintegrator.wbi_helpers import execute_sparql_query

import config
from src import EntityID, console

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
if results is not None:
    for result in results["results"]["bindings"]:
        item = str(EntityID(result["item"]["value"]))
        title = result["title"]["value"]
        language = result["title"]["xml:lang"]
        detected_language = detect(title)
        if language != detected_language:
            console.print(f"[red]{item} {title} {language} {detected_language}[red]")
        else:
            console.print(f"[green]{item} {title} {language} {detected_language}[green]")
        #exit(0)