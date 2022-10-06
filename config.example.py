import logging
import tempfile
from typing import List

# Rename this file to __init__.py

# Add your botpassword and login here:
username = ""
password = ""

# General settings
automatically_approve_jobs_with_less_than_fifty_matches = False
loglevel = logging.WARNING
wiki_user = "User:Username"  # Change this to your username
wd_prefix = "http://www.wikidata.org/entity/"
endpoint = "https://query.wikidata.org/sparql"
user_agent = f"ItemSubjector (https://github.com/dpriskorn/ItemSubjector), {wiki_user}"
tool_url = "https://github.com/dpriskorn/ItemSubjector"
tool_wikipage = "Wikidata:Tools/ItemSubjector"
login_instance = None
# This should work for all platforms except kubernetes
job_pickle_file_path = f"{tempfile.gettempdir()}/pickle.dat"
# job_pickle_file_path = "~/pickle.dat"  # works on kubernetes

"""
Settings for items
"""

list_of_allowed_aliases: List[str] = []  # Add elements like this ["API"]

# Scholarly items settings
blocklist_for_scholarly_items: List[str] = [
    "Q28196260",
    "Q28196260",
    "Q28196266",  # iodine
    "Q27863114",  # testosterone
    "Q28196266",
    "Q28196260",
    "Q109270553",  # dieback
]
no_alias_for_scholarly_items: List[str] = [
    "Q407541",
    "Q423930",
    "Q502327",
    "Q416950",
    "Q95566669",  # hypertension
]
