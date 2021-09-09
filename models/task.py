from models.wikidata import Items


class Task:
    """This class holds the tasks presented to the
    user in the menu, the question asked when working
    and the sparql query needed as a method"""
    label: str
    question: str
    items: Items

    def __init__(self,
                 label: str = None,
                 question: str = None,
                 items: Items = None):
        if label is None:
            raise ValueError("Got no label")
        if question is None:
            raise ValueError("Got no question")
        if items is None:
            raise ValueError("Got no items class")
        self.label = label
        self.question = question
        self.items = items

    def __str__(self):
        return f"{self.label}"
