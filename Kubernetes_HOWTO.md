# How to setup ItemSubjector on Kubernetes
So you have access to a cluster and you want to run ItemSubjector in batch mode?

The guide below is adapted to the specifics of the Wikimedia cluster, 
but it should be possible to run on any Kubernetes cluster with a python >=3.8 pod.

## Wikimedia Cloud VCS Kubernetes setup
1) setup a toolforge account, see https://wikitech.wikimedia.org/wiki/Portal:Toolforge/Quickstart

## Windows
2) download PuTTY (e.g. with chocolatey.org)
3) [generate a SSH key using PuTTY](https://phoenixnap.com/kb/generate-ssh-key-windows-10) and give it a password as per WMF instructions here https://www.mediawiki.org/wiki/Gerrit/Tutorial#Generate_a_new_SSH_key
4) log in via PuTTY to url `dev-buster.toolforge.org` on port 22, see https://www.mediawiki.org/wiki/Toolserver:Logging_in#Logging_in_with_PuTTY. Ask for help in [Telegram](https://t.me/wmcloudirc) or IRC if you don't succeed

## Create a tool
1) Now log into the [toolserver webinterface](https://toolsadmin.wikimedia.org/tools/) and [create a tool](https://wikitech.wikimedia.org/wiki/Portal:Toolforge/Tool_Accounts#Create_tools_with_Tool_Accounts). E.g. "itemsubjector-YOUR_USERNAME"

## Become tool
After the tool is registered log out of SSH and back in.

1) become the tool `become TOOLNAME`

## GNU screen
The author recommends GNU screen to make it possible 
to have multiple "windows" and to be able to easily attach/detach

If you don't know how to use screen your life can become pretty miserable. Read up and watch e.g. https://www.youtube.com/results?search_query=gnu+screen

The author recommends:
- increasing the scrollback buffer by invoking with e.g. `screen -D -RR -h 5000`
- using `ctrl + a ESC` to scroll back and inspect matches

## Clone ItemSubjector
run `git clone https://github.com/dpriskorn/ItemSubjector.git itemsubjector && cd itemsubjector`

## Fix the execution right on the scripts
Run this in the itemsubjector-folder: 
`chmod +x *.sh`

## Setup setup.sh
`ln -s setup_environment.sh ~setup.sh`

## Setup ItemSubjector
The bastion only has python 3.7 installed which is not enough to run the new version of WikibaseIntegrator :/
This means that the requirements file from poetry cannot be used on the bastion until the python version is updated.

Run this command instead
`$ pip install wikibaseintegrator==0.12.1 console-menu pydantic rich pandas`

## Prepare a set of jobs
Follow the README, but leave out "poetry run" e.g. run `python itemsubjector.py -a Q108801503` instead

## Start a batch on Kubernetes
run `./create_kubernettes_job_and_watch_the_log.sh 1`

This will start he k8s job and show you the tail of the output. 
By using `watch` the output will be updated every 2 seconds 
which makes it easy for you to get an idea of the progress.