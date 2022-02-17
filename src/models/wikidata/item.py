import logging
from typing import List, Optional

from wikibaseintegrator import WikibaseIntegrator  # type: ignore
from wikibaseintegrator import wbi_config  # type: ignore
from wikibaseintegrator.models import Alias  # type: ignore

import config
from src.models.task import Task
from src.models.wikidata.entity import Entity
from src.models.wikidata.entiyt_id import EntityID

wbi_config.config['USER_AGENT'] = config.user_agent


class Item(Entity):
    """This represents an item in Wikidata
    We always work on one language at a time,
    so don't bother with languages here and keep to simple strings"""
    id: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    aliases: Optional[List[str]] = None

    def __init__(self,
                 id: str = None,
                 json: str = None,
                 label: str = None,
                 description: str = None,
                 aliases: List[str] = None,
                 task: Task = None):
        if json is not None:
            self.parse_json(json)
        else:
            if id is not None:
                self.id = str(EntityID(id))
            if description is None and label is None and aliases is None:
                logging.debug("No of description, label or aliases received")
                if task is None:
                    raise ValueError("Got no task")
                if not isinstance(task, Task):
                    raise ValueError("task was not a Task object")
                self.fetch_label_and_description_and_aliases(task=task)
            elif label is None or aliases is None:
                raise ValueError("This is not supported. "
                                 "Either both state the label and "
                                 "aliases or None of them")
            else:
                self.label = label
                self.aliases = aliases
                self.description = description

    def __str__(self):
        return f"{self.label}, see {self.url()}"

    def parse_json(self, json):
        """Parse the WDQS json"""
        logger = logging.getLogger(__name__)
        try:
            logger.debug(f'item_json:{json["item"]}')
            self.id = str(EntityID(json["item"]["value"]))
        except KeyError:
            pass
        try:
            logger.debug(json["itemLabel"])
            self.label = (json["itemLabel"]["value"])
        except KeyError:
            logger.info(f"no label found")

    def parse_from_wdqs_json(self, json):
        """Parse the json into the object"""
        for variable in json:
            logging.debug(variable)
            if variable == "item":
                self.id = variable
            if variable == "itemLabel":
                self.label = variable

    def fetch_label_and_description_and_aliases(self,
                                                task: Task = None):
        """Fetch label and aliases in the task language from the Wikidata API"""
        if task is None:
            raise ValueError("task was None")
        if not isinstance(task, Task):
            raise ValueError("task was not a Task object")
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
