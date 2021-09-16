from helpers.enums import SupportedLanguageCode
from models.riksdagen_documents import RiksdagenDocumentLabels
from models.scholarly_articles import ScholarlyArticleLabels
from models.task import Task

scholarly_labels = ScholarlyArticleLabels()
riksdagen_labels = RiksdagenDocumentLabels()
tasks = [
    Task(
        id="scholarly_articles",
        label="Add main subject to scholarly articles",
        question="Is this a valid subject for this article?",
        labels=scholarly_labels,
        language_code=SupportedLanguageCode.ENGLISH
    ),
    Task(
        id="riksdagen_documents",
        label="Add main subject to documents from Riksdagen",
        question="Is this a valid subject for this document?",
        labels=riksdagen_labels,
        language_code=SupportedLanguageCode.SWEDISH
    )
]