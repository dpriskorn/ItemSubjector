# ItemSubjector
*still in BETA*

Tool made to add main subject statements to 
items based on a heuristic matching the subject with the title of the item. 
![bild](https://user-images.githubusercontent.com/68460690/133230724-40a610b7-5557-4b2b-b66e-2d80ca89e90d.png)
*The tool running in PAWS adding manually found main subject QIDs*

**Warning: This tool enables you to make a lot of bad edits quickly. 
Please check and read the output carefully before validating batches.**

# Features
This tool has the following features:
* Adding a list of manually supplied main subjects to items 
  (for now scholarly articles and documents 
  from Riksdagen are supported)
* Matching against 136.000 existing main subjects and adding them to scholarly articles
* Batch mode that can be used together with the above features and be run non-interactively 
  e.g. in the Wikimedia Cloud Services kubernetes beta cluster

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
Clone the repo (see below for an example command for PAWS).

You can also download PyCharm and go to the Git-menu 
and select "Clone..." and enter the clone url 
`https://github.com/dpriskorn/ItemSubjector.git`

Go into the directory and run `pip install -r requirements.txt` 
to install all requirements or have PyCharm do it for you

## PAWS
The tool runs in PAWS with no known issues.
* log in to PAWS
* open a terminal
* run `git clone https://github.com/dpriskorn/ItemSubjector.git .itemsubjector && cd .itemsubjector` 
  <- note the dot in front of the directory name 
  that hides it from publication.
* run `pip install -r requirements.txt`

## Wikimedia Cloud Services Kubernetes Beta cluster
See the batch commands below and 
https://phabricator.wikimedia.org/T285944#7373913 
for details.

There is a `setup_environment.sh` in the root of this repo that can help 
you prepare the pod/container so that the tool will work.


# Setup
Like my other tools, copy config.example.py -> 
config.py and enter the botusername 
(e.g. So9q@itemsubjector) and the botpassword
* e.g. `cp config.example.py config.py && nano config.py`

Note: `nano` is a console editor. When done editing press 
`ctrl+x` to quit and `y` to save.
  
# Use
This tool helps by adding the 
validated or supplied QID to all 
scientific articles where the 
search string appears (with 
spaces around it or in the beginning
or end of the string) in the label 
of the target item (e.g. scientific article).

## Adding QIDs manually
*Always run the most precise subjects first*

Run the script with the -a or --add argument 
followed by one or more QIDs or URLS:
* `python itemsubjector.py -l Q108528107` or
* `python itemsubjector.py -l https://www.wikidata.org/wiki/Q108528107`
  
Here is a more advanced example:
The first is *metastatic breast cancer* which is a 
subclass of the second *breast cancer*
* `python itemsubjector.py -a Q108528107 && python itemsubjector.py -a Q128581`

*Note the changes to the command line above since v0.1. 
Because of internal changes related to jobs 
you have to run the script again like above 
to avoid adding the broader subject to the 
more specific one.*

By adding the most specific subjects first 
we avoid redundancy since we 
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

### Show links column in table of search expressions 
This is handy if you want to look them up easily.

Usage example:
`python itemsubjector.py -l Q34 --show-search-urls` 
(the shorthand `-su` also works)

### Show links column in table of search expressions 
This is handy if you want to look them up easily.

Usage example:
`python itemsubjector.py -l Q34 --show-item-urls` 
(the shorthand `-iu` also works)

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

## Deleting existing main subjects from items
Sometimes users run a batch with a broad subject without 
realising that a narrower subject would be more suitable.
In those cases you can now delete the broad QID like this:

Usage example:
`python itemsubjector.py -d QID-to-delete -f QID-of-more-specific-main-subject-`

The tool will look up all items having both the QID-to-delete and 
QID-of-more-specific-main-subject and delete the former from P921.
It will only delete statements that have 
"based on heuristic"-: "inferred from title".

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
usage: itemsubjector.py [-h] [-a ADD [ADD ...]] [-na] [-p] [-r] [-rm] [-m] [-w] [-su] [-iu] [-d [DELETE]] [-f FROM_ITEMS_WITH [FROM_ITEMS_WITH ...]]

ItemSubjector enables working main subject statements on items based on a
heuristic matching the subject with the title of the item.

It also enables your to delete main subjects on items if they have at least
one other main subject.

Example adding one QID:
'$ itemsubjector.py Q1234'

Example adding one QID and prepare a job list to be run non-interactively later:
'$ itemsubjector.py Q1234 -p'

Example adding random QIDs from a list of main subjects extracted from 2 million scholarly articles:
'$ itemsubjector.py -m'

Example adding random QIDs from a list of main subjects extracted from 2 million scholarly articles
and prepare a job list:
'$ itemsubjector.py -m -p'

Example removing a QID from a P921 on items that have another (more specific QID in P921):
'$ itemsubjector.py -d Q1234 -f Q1'


optional arguments:
  -h, --help            show this help message and exit
  -a ADD [ADD ...], --add ADD [ADD ...], --qid-to-add ADD [ADD ...]
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
  -su, --show-search-urls
                        Show an extra column in the table of search strings with links
  -iu, --show-item-urls
                        Show an extra column in the table of items with links
  -d [DELETE], --delete [DELETE]
                        Delete a specific QID from P921 on the items that have a P921 with one of the values specified with --has-main-subject
  -f FROM_ITEMS_WITH [FROM_ITEMS_WITH ...], --from-items-with FROM_ITEMS_WITH [FROM_ITEMS_WITH ...], --has-main-subject FROM_ITEMS_WITH [FROM_ITEMS_WITH ...]
                        Work on a subset of items having any of these P921-values
```
# License
GPLv3+

# Note about discontinued NER matching and extraction of n-grams
Version 0.1 had NER matching based on n-grams found via NLP.
Unfortunately the data available from Wikidatas CirrusSearch has a 
hardcoded limit of 10.000 and that makes extracting 
meaningful high-quality n-grams difficult.

The author considered using the dumps to workaround this 
issue, but decided it was not worth the effort since with 
the new features humans can easily make jobs that 
improves thousands of items without relying on NLP or NER.