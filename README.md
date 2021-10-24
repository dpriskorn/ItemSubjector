# ItemSubjector
The purpose of this tool is to add main subject statements to Wikidata 
items based on a heuristic matching the subject with the title of the item. 
![bild](https://user-images.githubusercontent.com/68460690/133230724-40a610b7-5557-4b2b-b66e-2d80ca89e90d.png)
*The tool running in PAWS adding manually found main subject QIDs*

# Background
As of september 2021 there were 37M scientific articles in Wikidata, but 27M of them were missing any main 
subject statement. That makes them very hard to find for scientists which is bad for science, 
because building on the work of others is essential in the global scientific community.

# Features
This tool has the following features:
* Adding a list of manually supplied main subjects to a few selected subgraphs 
  (These currently include a total of 37M items with scholarly items being the biggest subgraph by far).
* Matching against a set of items fetched via a SPARQL query.
* Matching against a downloaded set of existing main subjects and adding them to more scholarly articles
* Batch mode that can be used together with the above features and be run non-interactively 
  e.g. in the Wikimedia Cloud Services Kubernetes Beta cluster

It supports 
[Wikidata:Edit groups](https://www.wikidata.org/wiki/Wikidata:Edit_groups) 
so that batches can easily be undone later if needed. 
Click "details" in the summary of edits to see more.

# Installation
Download the release tarball or clone the tool using Git.

## Clone the repository 
`git clone https://github.com/dpriskorn/ItemSubjector.git && cd ItemSubjector`

and run

`pip install -r requirements.txt`

to install all requirements.

Then checkout the latest release. 

`git checkout v0.x` where x is the latest number on the release page.

## PAWS
The tool runs in PAWS with no known 
issues.
* log in to PAWS
* open a terminal
* run `git clone https://github.com/dpriskorn/ItemSubjector.git .itemsubjector && cd .itemsubjector && pip install -r requirements.txt` 
  <- note the dot in front of the directory name 
  that hides it from publication which is crucial to 
  avoid publication of your login credentials.
* follow the details under Setup below

*Note: PAWS is not ideal for batch jobs unless you 
are willing to keep your browser tab open for the 
whole duration of the job. Consider using Kubernetes 
instead, see below*

## Wikimedia Cloud Services Kubernetes Beta cluster
See [Kubernetes_HOWTO.md](Kubernetes_HOWTO.md)

# Setup
Like my other tools, copy config.example.py -> 
config.py and enter the botusername 
(e.g. So9q@itemsubjector) and password
* e.g. `cp config.example.py config.py && nano config.py`

*GNU Nano is an editor, press `ctrl+x` when you are done and `y` to save your changes*

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
* `python itemsubjector.py -a Q108528107` or
* `python itemsubjector.py -a https://www.wikidata.org/wiki/Q108528107`

*Note since v0.2 you should not add subjects that are subclass 
of each other in one go. 
This is because of internal changes related to job handling*

Add the narrow first and then the broader like this:
* `python itemsubjector.py -a narrow-QID && python itemsubjector.py -l broader-QID`

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
`python itemsubjector.py -a Q34 --no-aliases` 
(the shorthand `-na` also works)

### Disable search expression confirmation
Avoid the extra question "Do you want to continue?":

Usage example:
`python itemsubjector.py -a Q34 --no-confirmation` 
(the shorthand `-nc` also works)

### Show links column in table of search expressions 
This is handy if you want to look them up easily.

Usage example:
`python itemsubjector.py -a Q34 --show-search-urls` 
(the shorthand `-su` also works)

### Show links column in table of search expressions 
This is handy if you want to look them up easily.

Usage example:
`python itemsubjector.py -a Q34 --show-item-urls` 
(the shorthand `-iu` also works)

### Limit to scholarly articles without main subject
Usage example:
`python itemsubjector.py -l Q34 --limit-to-items-without-p921` 
(the shorthand `-w` also works)

## Matching main subjects based on a SPARQL query.
The tool can create a list of jobs by picking random subjects from a
users SPARQL query.

Usage example for diseases:
`python itemsubjector.py -iu --sparql "SELECT ?item WHERE {?item wdt:P31 wd:Q12136.}"`

This makes it much easier to cover a range a subjects. 
This example query returns ~5000 items to match :)

## Matching against existing main subjects
*Warning: This often proposes too broad subjects 
that should most probably not be added as main subjects to all matches, 
but instead be broken down into narrower subjects*

The tool can create a list of jobs by picking random subjects from a
big list fetched from WDQS.

This enables the user to quickly build up a big list of jobs to run 
and improve the graph by improving the coverage on existing subjects.

To set it up run:
* `python fetch_main_subjects.py` by default it fetches 100,000 main 
  subjects and saves them after removing duplicates 
  (this usually results in about 10,000 unique subjects which should 
  be enough to get started)
  The script implements a random offset so running it again will yield 
  a different set of subjects, but please don't run it too often.

Usage example:
* `python itemsubjector.py -m`

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
usage: itemsubjector.py [-h] [-a ADD [ADD ...]] [-na] [-nc] [-p] [-r] [-rm] [-m] [-w] [-su] [-iu] [--sparql [SPARQL]] [--debug-sparql]

ItemSubjector enables working main subject statements on items based on a
heuristic matching the subject with the title of the item.

Example adding one QID:
'$ itemsubjector.py -l Q1234'

Example adding one QID and prepare a job list to be run non-interactively later:
'$ itemsubjector.py -l Q1234 -p'

Example adding random QIDs from a list of main subjects extracted from 2 million scholarly articles:
'$ itemsubjector.py -m'

Example adding random QIDs from a list of main subjects extracted from 2 million scholarly articles
and prepare a job list:
'$ itemsubjector.py -m -p'

Example working on all diseases:
'$ itemsubjector.py --sparql "SELECT ?item WHERE {?item wdt:P31 wd:Q12136.}"'


optional arguments:
  -h, --help            show this help message and exit
  -a ADD [ADD ...], --add ADD [ADD ...], --qid-to-add ADD [ADD ...]
                        List of QIDs or URLs to Q-items that are to be added as main subjects on scientific articles. Always add the most specific ones first. See the README
                        for examples
  -na, --no-aliases     Turn off alias matching
  -nc, --no-confirmation
                        Turn off confirmation after displaying the search expressions, before running the queries.
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
  --sparql [SPARQL]     Work on main subject items returned by this SPARQL query. Note: "?item" has to be in selected for it to work.
  --debug-sparql        Enable debugging of SPARQL queries.
```
# License
GPLv3+

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

Thanks also to **jsamwrites** for help with testing and suggestions 
for improvement.