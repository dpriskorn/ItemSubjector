from typing import List, Optional

from wikibaseintegrator import WikibaseIntegrator  # type: ignore
from wikibaseintegrator import wbi_config  # type: ignore
from wikibaseintegrator.models import Alias  # type: ignore

import config
from src.models.task import Task
from src.models.wikimedia.wikidata.entity import Entity

wbi_config.config['USER_AGENT'] = config.user_agent


class Item(Entity):
    """This represents an item in Wikidata
    We always work on one language at a time,
    so we don't bother with languages here and keep to simple strings"""
    description: Optional[str] = None
    aliases: Optional[List[str]] = None

    def __str__(self):
        return f"{self.label}, see {self.url()}"

    def fetch_label_and_description_and_aliases(self,
                                                task: Task = None):
        """Fetch label and aliases in the task language from the Wikidata API"""
        if task is None:
            raise ValueError("task was None")
        if not isinstance(task, Task):
            raise ValueError("task was not a Task object")
        if task.language_code is None:
            raise ValueError("task.language_code was None")
        from src.helpers.console import console
        with console.status(f"Fetching {task.language_code.name.title()} label and aliases from the Wikidata API..."):
            wbi = WikibaseIntegrator()
            item = wbi.item.get(self.id)
            label = item.labels.get(task.language_code.value)
            if label is not None:
                self.label = str(label)
            description = item.descriptions.get(task.language_code.value)
            if description is not None:
                self.description = str(description)
            aliases: List[Alias] = item.aliases.get(task.language_code.value)
            # logging.debug(f"aliases from wbi:{item.aliases.get('en')}")
            if aliases is not None:
                self.aliases = []
                for alias in aliases:
                    self.aliases.append(str(alias))
                    # logging.debug(f"appended:{alias.value}")
                # logging.debug(f"aliases:{self.aliases}")
