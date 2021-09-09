import logging

import requests

# import spacy
# from spacy import displacy
import config
from helpers.console import console
from helpers.menus import select_task
from models.task import Task
from models.wikidata import Item

logging.basicConfig(level=logging.DEBUG)

# pseudo code
# let user choose what to work on ie.
# let user choose language and subgraph
# e.g. Swedish documents from Riksdagen
# e.g. English scientific articles
# loop:
# get some items with labels
# do NER on a label
# let the user chose 1 meaningful match
# download all items without main subject matching the matched entity
# and with the entity label in the item label
# upload main subject to all


def find_entities(item: Item = None):
    logger = logging.getLogger(__name__)
    if item is None:
        raise ValueError("Got no item")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Accept': '*/*',
        'Accept-Language': 'sv-SE,sv;q=0.8,en-US;q=0.5,en;q=0.3',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://opentapioca.org',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://opentapioca.org/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }
    data = {
      'query': item.label
    }
    response = requests.post('https://opentapioca.org/api/annotate', headers=headers, data=data)
    if response.status_code == 200:
        console.print("Got 200")
        json_data = response.json()
        console.print(json_data)
        return json_data
    else:
        raise Exception(f"Got f{response.status_code} from opentapioca")


def process_entities(json_data):
    #exit(0)
    for annotation in json_data["annotations"]:
        # we select first tag only for now
        tag = annotation["tags"][0]
        qid = tag["id"]
        label = tag["label"]
        description = tag["desc"]
        console.print(f"label:{label}\n"
                      f"desc:{description}\n"
                      f"{config.wd_prefix+qid}\n")
    # give the user a list to choose from
    # when the user has chosen something, find other
    # scientific articles with this entity label (using elastic search?)
    # and that does not have this entity as main subject already
    # and upload to all


def main():
    # for now only English
    # chose_language()
    task: Task = select_task()
    if task is None:
        raise ValueError("Got no task")
    for item in task.items.list:
        json_data = find_entities(item=item)
        process_entities(json_data)


if __name__ == "main":
    main()

# NER = spacy.load("en_core_web_sm")
# raw_text=("The Indian Space Research Organisation or is the "
#           "national space agency of India, headquartered in Bengaluru. "
#           "It operates under Department of Space which is directly "
#           "overseen by the Prime Minister of India "
#           "while Chairman of ISRO acts as executive of DOS as well.")
# text1= NER(raw_text)
# for word in text1.ents:
#     print(word.text,word.label_)
#Swedish
# todo download # https://data.kb.se/datasets/2020/10/swedish_nlp/spacy/sv_pipeline-0.0.0.tar.gz >800 MB
# sv_NER = spacy.load("sv_pipeline")
# raw_text=("Rymdfart sker med rymdsonder och rymdfarkoster uppskjutna med rymdraketer och "
#           "har sedan sitt eget framdrivningssystem avsett att nå rymdfarkostens beräknade mål. "
#           "Mycket av dagens rymdforskning går ut på att studera jorden och dess miljö. "
#           "Man genomför forskning både inom biologiska områden och inom materialforskning.")
# text1= sv_NER(raw_text)
# for word in text1.ents:
#     print(word.text,word.label_)
