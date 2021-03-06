import logging
import tempfile

# Rename this file to __init__.py

# Add your botpassword and login here:

username = ""
password = ""

# Settings
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
