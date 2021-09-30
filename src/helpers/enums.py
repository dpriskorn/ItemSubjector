from enum import Enum, auto


class SupportedLanguageCode(Enum):
    ENGLISH = "en"
    SWEDISH = "sv"


class TaskIds(Enum):
    SCHOLARLY_ARTICLES = auto()
    RIKSDAGEN_DOCUMENTS = auto()
    THESIS = auto()