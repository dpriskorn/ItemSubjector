import argparse
from typing import List, Optional

from wikibaseintegrator import WikibaseIntegrator  # type: ignore
from wikibaseintegrator import wbi_config  # type: ignore
from wikibaseintegrator.models import Alias  # type: ignore

import config
from src.models.task import Task
from src.models.wikimedia.wikidata.entity import Entity

wbi_config.config["USER_AGENT"] = config.user_agent


class Item(Entity):
    """This represents an main_subject_item in Wikidata
    We always work on one language at a time,
    so we don't bother with languages here and keep to simple strings"""

    aliases: Optional[List[str]] = None
    args: Optional[argparse.Namespace] = None
    confirmation: bool = False
    description: Optional[str] = None
    task: Optional[Task] = None

    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        return f"{self.label}, see {self.url}"

    def __fetch_label_and_description_and_aliases__(self, task: Task = None):
        """Fetch label and aliases in the task language from the Wikidata API"""
        if not self.task:
            raise ValueError("self.task was None")
        if not isinstance(self.task, Task):
            raise ValueError("self.task was not a Task object")
        if self.task.language_code is None:
            raise ValueError("self.task.language_code was None")
        from src.helpers.console import console

        with console.status(
            f"Fetching {self.task.language_code.name.title()} label and aliases from the Wikidata API..."
        ):
            wbi = WikibaseIntegrator()
            if not self.id:
                id = self.id
            item = wbi.item.get(id)
            label = item.labels.get(self.task.language_code.value)
            if label:
                self.label = str(label)
            description = item.descriptions.get(self.task.language_code.value)
            if description:
                self.description = str(description)
            aliases: List[Alias] = item.aliases.get(self.task.language_code.value)
            # logging.debug(f"aliases from wbi:{main_subject_item.aliases.get('en')}")
            if aliases:
                self.aliases = []
                for alias in aliases:
                    self.aliases.append(str(alias))
                    # logging.debug(f"appended:{alias.value}")
                # logging.debug(f"aliases:{self.aliases}")

    def __strip_qid_prefix__(self):
        if "https://www.wikidata.org/wiki/" in self.id:
            self.id = self.id[30:]
        if "http://www.wikidata.org/entity/" in self.id:
            self.id = self.id[31:]
        # logger.debug(f"id:{id}")
