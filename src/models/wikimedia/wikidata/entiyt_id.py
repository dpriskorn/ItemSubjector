import logging

import config
from src.models.wikimedia.wikidata.enums import WikidataNamespaceLetters


# TODO convert this to special constr type with a validator
class EntityId:
    letter: WikidataNamespaceLetters
    # This can be e.g. "32698-F1" in the case of a lexeme
    rest: str

    def __init__(self, entity_id: str):
        logger = logging.getLogger(__name__)
        if entity_id is not None:
            # Remove prefix if found
            if config.wd_prefix in entity_id:
                logger.debug("Removing prefix")
                entity_id = entity_id.replace(config.wd_prefix, "")
            if len(entity_id) > 1:
                logger.info(f"entity_id:{entity_id}")
                self.letter = WikidataNamespaceLetters(entity_id[0])
                self.rest = entity_id[1:]
            else:
                raise ValueError("Entity ID was too short.")
        else:
            raise ValueError("Entity ID was None")

    def __str__(self):
        return f"{self.letter.value}{self.rest}"

    # def extract_wdqs_json_entity_id(self, json: Dict, sparql_variable: str):
    #     self.__init__(json[sparql_variable]["value"].replace(
    #         config.wd_prefix, ""
    #     ))
