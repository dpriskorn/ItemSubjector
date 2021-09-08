from rich.console import Console
console = Console()
# import spacy
# from spacy import displacy

baseurl = "https://www.wikidata.org/wiki/"

# let user choose language and subgraph
# e.g. Swedish documents from Riksdagen
# e.g. English scientific articles
# get 20 items with labels from WD that has no "main subject"
# load the relevant model
# parse the first label
# if a NE is found
## ask user if it is correct
##

# Tests
# English
# NIF test with opentapioca
# from pynif import NIFCollection
# collection = NIFCollection(uri="https://opentapioca.org/api/nif")

# test annotate
import requests

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
