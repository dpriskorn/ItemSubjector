import logging
import tempfile

# Add your botpassword and login here:
from typing import List

username = ""
password = ""

# Settings
loglevel = logging.WARNING
wiki_user = "User:Username"  # Change this to your username
list_of_allowed_aliases: List[str] = []  # Add elements like this ["API"]
blocklist_for_scholarly_items: List[str] = [
    "Q28196260",  # alcohol
]
no_alias_for_scholarly_items: List[str] = []
wd_prefix = "http://www.wikidata.org/entity/"
endpoint = "https://query.wikidata.org/sparql"
user_agent = f"ItemSubjector (https://github.com/dpriskorn/ItemSubjector), {wiki_user}"
tool_url = "https://github.com/dpriskorn/ItemSubjector"
tool_wikipage = "Wikidata:Tools/ItemSubjector"
login_instance = None
# This should work for all platforms except kubernetes
job_pickle_file_path = f"{tempfile.gettempdir()}/pickle.dat"
# job_pickle_file_path = "~/pickle.dat"  # works on kubernetes
main_subjects_pickle_file_path = f"data/main_subjects.pkl"
