from helpers.enums import SupportedLanguageCode, TaskIds
from models.task import Task

# When adding a new task, also add it in the enum

tasks = [
    Task(
        id=TaskIds.SCHOLARLY_ARTICLES,
        label="Add main subject to scholarly articles",
        question="Is this a valid subject for this article?",
        language_code=SupportedLanguageCode.ENGLISH
    ),
    Task(
        id=TaskIds.RIKSDAGEN_DOCUMENTS,
        label="Add main subject to documents from Riksdagen",
        question="Is this a valid subject for this document?",
        language_code=SupportedLanguageCode.SWEDISH
    )
]
