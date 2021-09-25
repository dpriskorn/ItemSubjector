# ItemSubjector
*still in BETA*

Tool made to add main subject statements to 
items based on a heuristic matching the subject with the title of the item. 
![bild](https://user-images.githubusercontent.com/68460690/133230724-40a610b7-5557-4b2b-b66e-2d80ca89e90d.png)
*The tool running in PAWS adding manually found main subject QIDs*

# Features
This tool has the following features:
* Adding a list of manually supplied main subjects to items 
  (for now scholarly articles and documents 
  from Riksdagen are supported)
* Matching against 136.000 existing main subjects and adding them to scholarly articles
* Batch mode that can be used together with the above features and be run non-interactively 
  e.g. in the Wikimedia Cloud kubernetes beta cluster

It supports 
[Wikidata:Edit groups](https://www.wikidata.org/wiki/Wikidata:Edit_groups) 
so that batches can easily be undone later if needed.

# Thanks
During the development of this tool the author got a 
help multiple times from **Jan Ainali** and **Jon Søby**
with figuring out how to query the API using the 
CirrusSearch extensions and to remove more 
specific main subjects from the query results.

A special thanks also to **Magnus Sälgö** for his valuable input 
and ideas, e.g. to search for aliases also and to *Jean* and the 
incredibly
helpful people in the Wikimedia Cloud Services Support chat that
helped with making batch jobs run successfully.

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

## Wikimedia Cloud Services kubernetes beta cluster
See the batch commands below and 
https://phabricator.wikimedia.org/T285944#7373913 
for details.

There is a `setup_environment.sh` in the root of this repo that can help 
you prepare the pod/container so that the tool will work.


# Setup
Like my other tools, copy config.example.py -> 
config.py and enter the botusername 
(e.g. So9q@itemsubjector) and password
* e.g. `cp config.example.py config.py && nano config.py`

# Use
This tool helps by adding the 
validated or supplied QID to all 
scientific articles where the 
search string appears (with 
spaces around it or in the beginning
or end of the string) in the label 
of the target item (e.g. scientific article).

## Adding QIDs manually
*Always provide the most precise subjects first*

Run the script with the -l or --list argument 
followed by one or more QIDs or URLS:
* `python itemsubjector.py -l Q108528107` or
* `python itemsubjector.py -l https://www.wikidata.org/wiki/Q108528107`
  
Here is a more advanced example:
The first is *metastatic breast cancer* which is a 
subclass of the second *breast cancer*
* `python itemsubjector.py -l Q108528107 Q128581` or

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
subjects (with thousands of matches) 
and try to nail down specific 
subjects and add them first. If you are 
unsure, please ask on-wiki or in the 
[Wikicite Telegram group](https://meta.wikimedia.org/wiki/Telegram)

### Disable alias matching
Sometimes e.g. for main subjects like 
[Sweden](https://www.wikidata.org/wiki/Q34) 
it is necessary to disable alias matching to 
avoid garbage matches. 

Usage example:
`python itemsubjector.py -l Q34 --no-aliases` 
(the shorthand `-na` also works)

### Limit to scholarly articles without main subject
Usage example:
`python itemsubjector.py -l Q34 --limit-to-items-without-p921` 
(the shorthand `-w` also works)

## Matching against ~136.000 existing main subjects
The tool can create a list of jobs by picking random subjects from a
big list based on 2 million samples where ~136.000 distinct subjects
were found (see `data/`).

This enables the user to quickly build up a big list of jobs to run 
and improve the graph by improving the coverage on existing subjects.

Usage example:
`python itemsubjector.py -m`

By using this function the author in 2 minutes created a list with 6 jobs
improving a total of 10.000 articles. You can now make a list of jobs with
little effort and let them run all day/night.

## Batch job features
The tool can help prepare jobs and then run 
them later non-interactively. This enables the user
to submit them as jobs on the Wikimedia Cloud Service 
Beta Kubernetes cluster, so you don't 
have to run them locally if you don't want to.

See the commands below and 
https://phabricator.wikimedia.org/T285944#7373913 
for details.

*Note: if you quit/stop a list of jobs that are 
currently running, please remove the 
unfinished prepared jobs before preparing 
new jobs by running --remove-prepared-jobs*

## List of all options
This is the output of `itemsubjector.py -h`:
```buildoutcfg
usage: itemsubjector.py [-h] [-l LIST [LIST ...]] [-na] [-p] [-r] [-rm] [-m] [-w]

optional arguments:
  -h, --help            show this help message and exit
  -l LIST [LIST ...], --list LIST [LIST ...]
                        List of QIDs or URLs to Q-items that are to be added as main subjects on scientific articles. Always add the most specific ones first. See the README
                        for examples
  -na, --no-aliases     Turn off alias matching
  -p, --prepare-jobs    Prepare a job for later execution, e.g. in a job engine
  -r, --run-prepared-jobs
                        Run prepared jobs non-interactively
  -rm, --remove-prepared-jobs
                        Remove prepared jobs
  -m, --match-existing-main-subjects
                        Match from list of 136.000 already used main subjects on other scientific articles
  -w, --limit-to-items-without-p921
                        Limit matching to scientific articles without P921 main subject
```
# License
GPLv3+
