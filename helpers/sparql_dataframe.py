import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON


def query_wikidata(sparql_query, sparql_service_url):
    """Query the endpoint with the given query string
    and return the results as a pandas Dataframe."""
    # create the connection to the endpoint
    # Wikidata enforces now a strict User-Agent policy, we need to specify the agent
    # See here https://www.wikidata.org/wiki/Wikidata:Project_chat/Archive/2019/07#problems_with_query_API
    # https://meta.wikimedia.org/wiki/User-Agent_policy
    sparql = SPARQLWrapper(sparql_service_url, agent="Sparql Wrapper on PAWS, User:So9q")

    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)

    # ask for the result
    from helpers.console import console
    console.status("Fetching data from WDQS...")
    result = sparql.query().convert()
    return pd.json_normalize(result["results"]["bindings"])
