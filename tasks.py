from helpers.enums import SupportedLanguageCode, TaskIds
from models.riksdagen_documents import RiksdagenDocumentLabels
from models.scholarly_articles import ScholarlyArticleLabels
from models.task import Task

# When adding a new task, also add it in the enum

# scholarly_labels = ScholarlyArticleLabels()
# riksdagen_labels = RiksdagenDocumentLabels()
tasks = [
    Task(
        id=TaskIds.SCHOLARLY_ARTICLES,
        label="Add main subject to scholarly articles",
        question="Is this a valid subject for this article?",
        labels=ScholarlyArticleLabels(),
        language_code=SupportedLanguageCode.ENGLISH
    ),
    Task(
        id=TaskIds.RIKSDAGEN_DOCUMENTS,
        label="Add main subject to documents from Riksdagen",
        question="Is this a valid subject for this document?",
        labels=RiksdagenDocumentLabels(),
        language_code=SupportedLanguageCode.SWEDISH
    )
]
