import os

# Add your botpassword and login here:
username = ""
password = ""

# Global settings
version = "0.1"  # Don't touch this.
wd_prefix = "http://www.wikidata.org/entity/"
endpoint = "https://query.wikidata.org/sparql"
wiki_user = "User:So9q"  # Change this to your username
user_agent = f"ItemSubjector/{version} (https://github.com/dpriskorn/ItemSubjector), {wiki_user}"
tool_url = "https://github.com/dpriskorn/ItemSubjector"
tool_wikipage = "Wikidata:Tools/ItemSubjector"
login_instance = None
random_offset=0