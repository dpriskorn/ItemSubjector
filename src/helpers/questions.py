# from __future__ import annotations

from typing import TYPE_CHECKING

from src.helpers.console import console

if TYPE_CHECKING:
    from src.models.batch_jobs import BatchJob


def ask_add_to_job_queue(job: "BatchJob" = None):
    if not job:
        raise ValueError("job was None")
    if not job.main_subject_item:
        raise ValueError("job.main_subject_item was None")
    if not job.main_subject_item.label:
        raise ValueError("job.main_subject_item.label was None")
    if not job.main_subject_item.description:
        job.main_subject_item.description = ""
    if not job.main_subject_item.items:
        raise ValueError("items was None")
    if not job.main_subject_item.items.sparql_items:
        raise ValueError("sparql_items was None")
    return ask_yes_no_question(
        f"Do you want to add this job for "
        f"[magenta]{job.main_subject_item.label}: "
        f"{job.main_subject_item.description}[/magenta] with "
        f"{len(job.main_subject_item.items.sparql_items)} items to the queue? (see {job.main_subject_item.url})"
    )


def ask_discard_existing_job_pickle():
    return ask_yes_no_question(
        "A prepared sparql_items of jobs already exist, " "do you want to delete it?"
    )


def ask_yes_no_question(message: str):
    # https://www.quora.com/
    # I%E2%80%99m-new-to-Python-how-can-I-write-a-yes-no-question
    # this will loop forever
    while True:
        answer = console.input(message + " [Y/Enter/n]: ")
        if len(answer) == 0 or answer[0].lower() in ("y", "n"):
            if len(answer) == 0:
                return True
            else:
                # the == operator just returns a boolean,
                return answer[0].lower() == "y"

def ask_yes_no_modify_question(self, message: str):
    from src.helpers.menus import modify_aliases
    
    while True:
        answer = console.input(message + " [Y/Enter/n/m]: ")
        if len(answer) == 0 or answer[0].lower() in ("y", "n", "m"):
            if len(answer) == 0:
                return True
            elif answer == "m":
                modify_aliases(self)
                return True
            else:
                # the == operator just returns a boolean,
                return answer[0].lower() == "y"