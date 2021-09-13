# ItemSubjector
Tool made to add main subject statements to 
items based on the title using a home-brewed 
CirrusSearch-based Named Entity Recognition algorithm. 

# Thanks
During the development of this tool the author got a 
help multiple times from *Jan Ainali* and *Jon Søby*
with figuring out how to query the API using the 
CirrusSearch extensions and to remove more 
specific main subjects from the query results.

# Installation
Clone the repo and run

`pip install -r requirements.txt`

to install all requirements.

# Setup
Like my other tools, copy config.example.py -> 
config.py and enter the botusername 
(e.g. So9q@itemsubjector) and password

# Use
It has 2 modes:
1) automatic finding n-grams and trying to 
   detect items that match
2) user added main subject item

Both modes conclude by adding the 
validated or supplied QID to all 
scientific articles where the 
n-gram/label appears in the label 
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
and then exclude those when adding the 
more general subject afterwards.

This way we avoid redundancy since we 
want the most specific subjects on the 
items and not 
all the general ones above it in the 
classification system.

# License
GPLv3+