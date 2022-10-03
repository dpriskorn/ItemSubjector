from typing import Any

from src.models.wikimedia.wikidata.query import Query


class ArticleQuery(Query):
    # any here because of pydantic error
    main_subject_item: Any
