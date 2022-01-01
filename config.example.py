import logging
import tempfile
from pathlib import Path

# Add your botpassword and login here:
username = ""
password = ""

# Global settings
wiki_user = "User:Username"  # Change this to your username
logging.basicConfig(level=logging.WARNING)
version = "0.2"  # Don't touch this.
wd_prefix = "http://www.wikidata.org/entity/"
endpoint = "https://query.wikidata.org/sparql"
user_agent = f"ItemSubjector/{version} (https://github.com/dpriskorn/ItemSubjector), {wiki_user}"
tool_url = "https://github.com/dpriskorn/ItemSubjector"
tool_wikipage = "Wikidata:Tools/ItemSubjector"
login_instance = None
# This should work for all platforms except kubernetes
job_pickle_file_path = f"{tempfile.gettempdir()}/pickle.dat"
# job_pickle_file_path = "~/pickle.dat"  # works on kubernetes
main_subjects_pickle_file_path = f"data/main_subjects.pkl"
