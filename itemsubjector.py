import logging

import config
from src import ItemSubjector

logging.basicConfig(level=config.loglevel)
itemsubjector = ItemSubjector()
itemsubjector.run()
