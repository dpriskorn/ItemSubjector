# ItemSubjector
The purpose of this command-line tool is to add main subject statements to Wikidata 
items based on a heuristic matching the subject with the title of the item. 
![bild](https://user-images.githubusercontent.com/68460690/133230724-40a610b7-5557-4b2b-b66e-2d80ca89e90d.png)
*The tool running in PAWS adding manually found main subject QIDs*
![bild](https://user-images.githubusercontent.com/68460690/155840858-057292a5-8647-415f-8df3-7bbb90884dbc.png)
*Itemsubjector running GNU Screen on a Toolforge bastion with --limit 100000 and 
--sparql matching the WHO list of essential medicines.*

# Background
As of september 2021 there were 37M scientific articles in Wikidata, but 27M of them were missing any main 
subject statement. That makes them very hard to find for scientists which is bad for science, 
because building on the work of others is essential in the global scientific community.

To my knowledge none of the scientific search engines that are currently used in the scientific community rely on an
open graph editable by anyone and maintained by the community itself for the purpose of helping fellow
scientists find each others work. Wikipedia and Scholia can fill that gap but we need good tooling to curate the 
millions of items.

# Caveat 
This type of matching that ONLY takes the label and not the underlying structured
data into account is SUBOPTIMAL. You are very welcome to suggest or contribute improvements
so we can improve the tool to help you make better edits.

# Features
This tool has the following features:
* Adding a list of manually supplied main subjects to a few selected subgraphs 
  (These currently include a total of 37M items with scholarly items being the biggest subgraph by far).
* Matching against a set of items fetched via a SPARQL query.
* Matching up to a limit of items which together with Kubernetes makes it possible to start a query which 
collects jobs with items until the limit is reached and then ask for approval/decline of each job. This 
enables the user to create large batches of jobs with 100k+ items in total in a matter of minutes.
* Batch mode that can be used together with the above features and be run non-interactively 
  e.g. in the Wikimedia Cloud Services Kubernetes Beta cluster

It supports 
[Wikidata:Edit groups](https://www.wikidata.org/wiki/Wikidata:Edit_groups) 
so that batches can easily be undone later if needed. 
Click "details" in the summary of edits to see more.

# Installation
Download the latest release with:

`$ pip install itemsubjector`

# Alternative installation in venv
Download the release tarball or clone the tool using Git.

## Clone the repository 
`git clone https://github.com/dpriskorn/ItemSubjector.git && cd ItemSubjector`

Then checkout the latest release. 

`git checkout vx.x.x` where x is the latest number on the release page.

## Setup the environment

Make a virtual environment and set it up using poetry. If you don't have poetry installed run:
`$ pip install poetry`

and then setup everying with

`$ poetry install --without=dev`

to install all requirements in a virtual environment.

## PAWS
*Note: PAWS is not ideal for batch jobs unless you 
are willing to keep your browser tab open for the 
whole duration of the job. Consider using Kubernetes 
instead, see below*

The tool runs in PAWS with no known 
issues.
* log in to PAWS
* open a terminal
* run `git clone https://github.com/dpriskorn/ItemSubjector.git .itemsubjector && cd .itemsubjector && pip install poetry && poetry install --without=dev` 
  <- note the dot in front of the directory name 
  that hides it from publication which is crucial to 
  avoid publication of your login credentials.
* follow the details under Setup below


## Wikimedia Cloud Services Kubernetes Beta cluster
*Note: this is for advanced users experienced with a SSH console environment, ask in the [Telegram WikiCite group](https://meta.m.wikimedia.org/wiki/Telegram#Wikidata) if you need help*

See [Kubernetes_HOWTO.md](Kubernetes_HOWTO.md)

# Setup
Setup the config by copying config/config.example.py -> 
config/__init__.py and enter the botusername 
(e.g. So9q@itemsubjector) and password 
(first [create a botpassword](https://www.wikidata.org/wiki/Special:BotPasswords) 
for your account 
and make sure you give it the *edit page permission* 
and *high volume permissions*)
* e.g. `cp config_example.py config.py && nano config.py`

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

Run the script with the -a or --add argument 
followed by one or more QIDs or URLS:
* `poetry run python itemsubjector.py -a Q108528107` or
* `poetry run python itemsubjector.py -a https://www.wikidata.org/wiki/Q108528107`

*Note since v0.2 you should not add subjects that are subclass 
of each other in one go. 
This is because of internal changes related to job handling*

Add the narrow first and then the broader like this:
* `poetry run python itemsubjector.py -a narrow-QID && poetry run python itemsubjector.py -a broader-QID`

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
`poetry run python itemsubjector.py -a Q34 --no-aliases` 
(the shorthand `-na` also works)

### Disable search expression confirmation
Avoid the extra question "Do you want to continue?":

Usage example:
`poetry run python itemsubjector.py -a Q34 --no-confirmation` 
(the shorthand `-nc` also works)

### Show links column in table of search expressions 
This is handy if you want to look them up easily.

Usage example:
`poetry run python itemsubjector.py -a Q34 --show-search-urls` 
(the shorthand `-su` also works)

### Show links column in table of search expressions 
This is handy if you want to look them up easily.

Usage example:
`poetry run python itemsubjector.py -a Q34 --show-item-urls` 
(the shorthand `-iu` also works)

[//]: # (### Limit to scholarly articles without main subject)
[//]: # (Usage example:)
[//]: # (`poetry run python itemsubjector.py -a Q34 --limit-to-items-without-p921` )
[//]: # (&#40;the shorthand `-w` also works&#41;)

## Matching main subjects based on a SPARQL query.
The tool can create a list of jobs by picking random subjects from a
users SPARQL query.

Usage example for diseases:
`poetry run python itemsubjector.py -iu --sparql "SELECT ?item WHERE {?item wdt:P31 wd:Q12136. MINUS {?main_subject_item wdt:P1889 [].}}"`

This makes it much easier to cover a range a subjects. 
This example query returns ~5000 items to match :)

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
See `$ poetry run python itemsubjector.py -h` for all options.

# What I learned
* I used the black code-formatter for the first time in this project and 
it is a pleasure to not have to sit and manually format the code anymore.
  
* I used argparse for the first time in this project and how to type it 
  properly.
  
* This was one of the first of my projects that had scope creep. I have 
removed the QuickStatements export to simplify the program.
  
* This project has been used in a scientific paper I wrote together with 
[Houcemeddine Turki](https://scholia.toolforge.org/author/Q53505397)

## Rewrite 2022:
* Important to break down methods to 1 method 1 task to increase readability. -> helps reuse in other projects.
* Important to avoid resetting attributes and instantiate classes instead. -> helps reuse in other projects.
* Simplify as much as possible to keep the whole thing lean and avoid scope creep. -> helps reuse in other projects. (KISS-principle)
* Difficult to judge which features are used and which are not. User testing would be nice.
* UML diagrams are nice. They give a good quick overview.
* Removing options that no-one seems to use helps keeping it simple. It would be valuable to get better insight of how the 
program is used by the users. A discussion in github might help in this.

# Thanks
During the development of this tool the author got a 
help multiple times from **Jan Ainali** and **Jon Søby**
with figuring out how to query the API using the 
CirrusSearch extensions and to remove more 
specific main subjects from the query results.

A special thanks also to **Magnus Sälgö** and **Arthur Smith** for their
valuable input and ideas, e.g. to search for aliases also and to *Jean* and the 
incredibly
helpful people in the Wikimedia Cloud Services Support chat that
helped with making batch jobs run successfully.

Thanks also to **jsamwrites** for help with testing and suggestions 
for improvement and for using the tool to improve a ton of items :).

# License
GPLv3+

