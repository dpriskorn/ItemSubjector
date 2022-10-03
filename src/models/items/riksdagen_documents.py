from wikibaseintegrator.wbi_helpers import execute_sparql_query  # type: ignore

from src.models.items import Items
from src.models.wikimedia.wikidata.query.riksdagen_document import (
    RiksdagenDocumentQuery,
)


# logger = logging.getLogger(__name__)


class RiksdagenDocumentItems(Items):
    def fetch_based_on_label(self):
        self.execute_queries()
        self.print_total_items()

    def execute_queries(self):
        # Fetch all items matching the search strings
        for search_string in self.main_subject_item.search_strings:
            riksdagen_query = RiksdagenDocumentQuery(
                main_subject_item=self.main_subject_item, search_string=search_string
            )
            riksdagen_query.get_results()
            self.sparql_items.extend(riksdagen_query.items)
