import requests
from rich.console import Console
console = Console()
# import spacy
# from spacy import displacy

baseurl = "https://www.wikidata.org/wiki/"

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

def select_lexical_category():
    menu = SelectionMenu(WikidataLexicalCategory.__members__.keys(), "Select a lexical category")
    menu.show()
    menu.join()
    selected_lexical_category_index = menu.selected_option
    category_mapping = {}
    for index, item in enumerate(WikidataLexicalCategory):
        category_mapping[index] = item
    selected_lexical_category = category_mapping[selected_lexical_category_index]
    logger.debug(f"selected:{selected_lexical_category_index}="
                 f"{selected_lexical_category}")
    return selected_lexical_category


def select_language():
    menu = SelectionMenu(WikimediaLanguageCode.__members__.keys(), "Select a language")
    menu.show()
    menu.join()
    selected_language_index = menu.selected_option
    mapping = {}
    for index, item in enumerate(WikimediaLanguageCode):
        mapping[index] = item
    selected_language = mapping[selected_language_index]
    logger.debug(f"selected:{selected_language_index}="
                 f"{selected_language}")
    return selected_language

def get_entities():
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
      'query': "Patient Perspectives of Dignity, Autonomy and Control at the End of Life: Systematic Review and Meta-Ethnography"
    }

    response = requests.post('https://opentapioca.org/api/annotate', headers=headers, data=data)
    if response.status_code == 200:
        console.print("Got 200")
        json_data = response.json()
        console.print(json_data)
        return json_data


def process_entities():
    #exit(0)
    for annotation in json_data["annotations"]:
        # we select first tag only for now
        tag = annotation["tags"][0]
        qid = tag["id"]
        label = tag["label"]
        description = tag["desc"]
        console.print(f"label:{label}\n"
                      f"desc:{description}\n"
                      f"{baseurl+qid}\n")
    # give the user a list to choose from
    # when the user has chosen something, find other
    # scientific articles with this entity label (using elastic search?)
    # and that does not have this entity as main subject already
    # and upload to all


def main():

    get_entities()
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
