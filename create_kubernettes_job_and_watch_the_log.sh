# Usage: chmod +x this script and run like this "./create_kubernettes_job_and_watch_the_log.sh 1"
# Increment the job number yourself each time
toolforge-jobs run job$1 --image tf-python39 --command "/bin/sh -c -- '~/setup.sh && python3 ~/itemsubjector/itemsubjector.py -r'"
watch tail ~/job$1*
