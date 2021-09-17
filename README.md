# ItemSubjector
*still in BETA*

Tool made to add main subject statements to 
items based on the title using a home-brewed 
CirrusSearch-based Named Entity Recognition algorithm. 
![bild](https://user-images.githubusercontent.com/68460690/133230724-40a610b7-5557-4b2b-b66e-2d80ca89e90d.png)
*The tool running in PAWS adding manually found main subject QIDs*

# Features
This tool has the following features
* adding a list of main subjects to items 
  (for now only scholarly articles are supported)
* automatically extracting n-grams from labels of 10.000 articles 
  (this is not that powerful because users know better than scikit 
  what subjects are meaningful to have on our scientific articles)

It supports 
[Wikidata:Edit groups](https://www.wikidata.org/wiki/Wikidata:Edit_groups) 
so that batches can easily be undone if needed.

# Thanks
During the development of this tool the author got a 
help multiple times from **Jan Ainali** and **Jon Søby**
with figuring out how to query the API using the 
CirrusSearch extensions and to remove more 
specific main subjects from the query results.

A special thanks also to **Magnus Sälgö** for his valuable input 
and ideas, e.g. to search for aliases also.

# Installation
Clone the repo and run

`pip install -r requirements.txt`

to install all requirements.

## PAWS
The tool runs in PAWS with no known 
issues.
* log in to PAWS
* open a terminal
* run `git clone https://github.com/dpriskorn/ItemSubjector.git .itemsubjector && cd .itemsubjector` 
  <- note the dot in front of the directory name 
  that hides it from publication.
* run the pip-command above

# Setup
Like my other tools, copy config.example.py -> 
config.py and enter the botusername 
(e.g. So9q@itemsubjector) and password
* e.g. `cp config.example.py config.py && nano config.py`

# Use
It has 2 modes:
1) automatic finding n-grams and trying to 
   detect items that match (default if no
   arguments are given on the command line)
2) add main subject items to scholarly articles

Both modes conclude by adding the 
validated or supplied QID to all 
scientific articles where the 
n-gram or search string appears (with 
spaces around it) in the label 
of the target item (e.g. scientific article).

## Adding QIDs manually
*Always provide the most precise subjects first*

Run the script with the -l or -list argument followed by one or more QIDs:
* `python itemsubjector.py -l Q108528107`
  
Here is a more advanced example:
The first is *metastatic breast cancer* which is a 
subclass of the second *breast cancer*
* `python itemsubjector.py -l Q108528107 Q128581`

In this case the tool is smart enough 
(thanks to Jan Ainali) to first add 
*metastatic breast cancer* to items 
and then exclude those items when adding the 
more general subject afterwards.

This way we avoid redundancy since we 
want the most specific subjects on the 
items and not 
all the general ones above it in the 
classification system.

Please investigate before adding broad 
subjects and try to nail down specific 
subjects and add them first. If you are 
unsure, please ask on-wiki or in the 
[Wikicite Telegram group](https://meta.wikimedia.org/wiki/Telegram)

# License
GPLv3+
