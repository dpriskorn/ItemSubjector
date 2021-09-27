from wikibaseintegrator import wbi_config
from wikibaseintegrator.wbi_helpers import execute_sparql_query

import config
from src import console
from src.helpers.cleaning import strip_prefix
# Set User-Agent
from src.helpers.pickle import add_to_main_subject_pickle

wbi_config.config["USER_AGENT_DEFAULT"] = config.user_agent
console.print("Fetching 100,000 main subjects")
console.input("Press enter to continue")
subjects = []
for i in range(0, 100000, 10000):
    print(i)
    # title: Get main subjects used at least once on scholarly articles
    results = execute_sparql_query(f"""
SELECT ?subject
WHERE
{{
{{
SELECT * WHERE {{
    hint:Query hint:optimizer "None".
    ?item wdt:P31 wd:Q13442814;
          wdt:P921 ?subject.
}}
offset {i}
limit 10000
}}
MINUS{{
?item wdt:P31 wd:Q8054.  # protein
}}
MINUS{{
?item wdt:P279 wd:Q8054.  # protein
}}
MINUS{{
?item wdt:P31 wd:Q7187.  # gene
}}
MINUS{{
?item wdt:P279 wd:Q7187.  # gene
}}
}}
    """)
    if len(results) == 0:
        raise ValueError("No main subjects found")
    else:
        # print("adding lexemes to list")
        # pprint(results.keys())
        # pprint(results["results"].keys())
        # pprint(len(results["results"]["bindings"]))
        for result in results["results"]["bindings"]:
            # print(result)
            subjects.append(strip_prefix(result["subject"]["value"]))
            # exit(0)
console.print(f"{len(subjects)} fetched")
console.print("Filtering out duplicates")
subjects_without_duplicates = set()
for subject in subjects:
    subjects_without_duplicates.add(subject)
console.print(f"Saving {len(subjects_without_duplicates)} "
              f"to pickle '{config.main_subjects_pickle_file_path}' (overwriting)")
add_to_main_subject_pickle(subjects)
console.print("Done")