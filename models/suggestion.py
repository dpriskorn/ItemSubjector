from urllib.parse import quote

from models.ngram import NGram
from models.wikidata import Item, EntityID


class Suggestion(Item):
    ngram: NGram = None

    def __init__(self,
                 id: str = None,
                 label: str = None,
                 description: str = None,
                 ngram: NGram = None):
        if id is not None:
            self.id = str(EntityID(id))
        self.label = label
        self.description = description
        self.ngram: NGram = ngram

    def __str__(self):
        """Return label and description, the latter cut to 50 chars"""
        return (f"n-gram: [green][bold]{self.ngram.label}[/bold][/green]\n"
                f"label: [bold]{self.label}[/bold]\n"
                f"description: {self.description[:70]}\n"
                f"{self.url()}\n"
                f"{self.search_url()}")

    def url(self):
        return f"https://www.wikidata.org/wiki/{self.id}"

    def search_url(self):
        search_term = quote(f'"{self.ngram.label}"')
        return f"https://www.wikidata.org/w/index.php?search={search_term}"
