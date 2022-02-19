import logging
from typing import Optional

from pydantic import BaseModel
from wikibaseintegrator import WikibaseIntegrator  # type: ignore
from wikibaseintegrator import wbi_config
from wikibaseintegrator.datatypes import BaseDataType  # type: ignore
from wikibaseintegrator.wbi_enums import ActionIfExists  # type: ignore

import config

wbi_config.config['USER_AGENT'] = config.user_agent


class Entity(BaseModel):
    """Base entity with code that is the same for both items and lexemes"""
    id: Optional[str]
    label: Optional[str]

    def upload_one_statement_to_wikidata(self,
                                         statement: BaseDataType = None,
                                         summary: str = None,
                                         editgroups_hash: str = None):
        """Upload one statement and always append
        This mandates an editgroups hash to be supplied"""
        logger = logging.getLogger(__name__)
        if self.id is None:
            raise ValueError("no id on item")
        if statement is None:
            raise ValueError("Statement was None")
        if summary is None:
            raise ValueError("summary was None")
        if editgroups_hash is None:
            raise ValueError("editgroup_hash was None")
        if config.login_instance is None:
            raise ValueError("No login instance in config.login_instance")
        wbi = WikibaseIntegrator(login=config.login_instance)
        item = wbi.item.get(self.id)
        item.add_claims(
            [statement],
            action_if_exists=ActionIfExists.APPEND)
        result = item.write(
            summary=f"Added {summary} with [[{config.tool_wikipage}]] "
                    f"([[:toolforge:editgroups/b/CB/{editgroups_hash}|details]])"
        )
        logger.debug(f"result from WBI:{result}")

    def url(self):
        return f"http://www.wikidata.org/entity/{self.id}"
