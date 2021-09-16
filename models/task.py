from helpers.enums import SupportedLanguageCode, TaskIds


class Task:
    """This class holds the tasks presented to the
    user in the menu, the question asked when working
    and the sparql query needed as a method"""
    id: TaskIds
    label: str
    question: str
    labels = None  # typing: Labels
    language_code: SupportedLanguageCode

    def __init__(self,
                 id: TaskIds = None,
                 label: str = None,
                 question: str = None,
                 labels=None,
                 language_code: SupportedLanguageCode = None):
        if id is None:
            raise ValueError("Got no id")
        if label is None:
            raise ValueError("Got no label")
        if question is None:
            raise ValueError("Got no question")
        if labels is None:
            raise ValueError("Got no labels class")
        if language_code is None:
            raise ValueError("Got no language_code")
        self.id = id
        self.label = label
        self.question = question
        from models.wikidata import Labels
        self.labels: Labels = labels
        self.language_code = language_code

    def __str__(self):
        return f"{self.label}"
