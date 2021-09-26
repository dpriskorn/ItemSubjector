# from __future__ import annotations
import argparse
from dataclasses import dataclass
from typing import List

from wikibaseintegrator.datatypes import Item as ItemType

from helpers.calculations import calculate_random_editgroups_hash
from helpers.console import console
from models.batch_job import BatchJob
from models.task import Task
from models.wikidata import Item


@dataclass
class DeletionTarget:
    item: Item = None

    def __str__(self):
        """Return label and description, the latter cut to 50 chars"""
        if self.item is not None:
            string = (
                f"label: [bold]{self.item.label}[/bold]\n"
                f"aliases: {', '.join(self.item.aliases)}\n"
                f"description: {self.item.description[:70]}\n"
                f"{self.item.url()}\n"
            )

    def delete_from_items(self,
                          task: Task = None,
                          jobs: List[BatchJob] = None,
                          job_count: int = None):
        """Delete the QID from P921 on all items in the task.

        We calculate a new edit group hash each time this function is
        called so similar edits are grouped and easily be undone.

        This function is non-interactive"""
        if task is None:
            raise ValueError("task was None")
        if jobs is None:
            raise ValueError("jobs was None")
        if job_count is None:
            raise ValueError("job count was None")
        editgroups_hash: str = calculate_random_editgroups_hash()
        count = 0
        for target_item in task.items.list:
            count += 1
            with console.status(f"Removing main subject [green]{self.item.label}[/green] from {target_item.label}"):
                raise NotImplementedError("todo")
                main_subject_property = "P921"
                reference = ItemType(
                    "Q69652283",  # inferred from title
                    prop_nr="P887"  # based on heuristic
                )
                statement = ItemType(
                    self.item.id,
                    prop_nr=main_subject_property,
                    references=[reference]
                )
                target_item.upload_one_statement_to_wikidata(
                    statement=statement,
                    summary=f"[[Property:{main_subject_property}]]: [[{self.item.id}]]",
                    editgroups_hash=editgroups_hash
                )
            console.print(f"(job {job_count}/{len(jobs)})(item {count}/{len(task.items.list)}) "
                          f"Added '{self.item.label}' to {target_item.label}: {target_item.url()}")
            input("Press enter to continue")
