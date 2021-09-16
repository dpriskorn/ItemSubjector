import logging

import requests
from wikibaseintegrator.wbi_helpers import search_entities

import config
from models.wikidata import Item


class NGram:
    label: str
    frequency: int

    def __init__(self,
                 label: str = None,
                 frequency: int = None):
        self.label = label
        self.frequency = frequency

    def recognize_named_entity(self):  # typing: -> Suggestion
        if self.label is None:
            raise ValueError("ngram was None")
        # console.print(f"Results for {self.label}")
        search_expression = (
                "-haswbstatement:P31=Q13442814 " +  # scientific article
                "-haswbstatement:P31=Q5633421 " +  # journal
                # See
                f'"{self.label}"'
        )
        params = (
            ('format', 'json'),
            ('action', 'query'),
            ('list', 'search'),
            ('srprop', ''),
            ('srlimit', '10'),
            ('sroffset', '0'),
            ('srsearch', search_expression),
        )
        headers = {
            'User-Agent': config.user_agent,
        }
        response = requests.get('https://www.wikidata.org/w/api.php', headers=headers, params=params)
        if response.status_code == 200:
            # pprint(response.headers)
            data = response.json()
            # pprint(data)
            # Get the first QID
            try:
                qid = data["query"]["search"][0]["title"]
                search_results = search_entities(
                    qid,
                    language="en",
                    user_agent=config.user_agent,
                    dict_result=True
                )
                if search_results is not None:
                    first_result = search_results[0]
                    # pprint(first_result)
                    from models.suggestion import Suggestion
                    item = Item(
                        id=first_result["id"],
                        label=first_result["label"],
                        description=first_result["description"],
                    )
                    return Suggestion(
                        item=item,
                        ngram=self
                    )
            except IndexError:
                logging.debug(f"No results found for {self.label}")
        else:
            print(f"Error got {response.status_code}: {response.text}")
        # for result in search_results[0:1]:
        #    pprint(result["description"])
        # print("breaking")
        # break
