# from __future__ import annotations

import logging

from pydantic import BaseModel
from wikibaseintegrator import WikibaseIntegrator  # type: ignore
from wikibaseintegrator.datatypes import Item as ItemType  # type: ignore
from wikibaseintegrator.models import Claim  # type: ignore
from wikibaseintegrator.wbi_helpers import search_entities  # type: ignore

logger = logging.getLogger(__name__)


class Suggestion(BaseModel):
    pass
