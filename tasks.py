from models.scholarly_articles import ScholarlyArticleLabels
from models.task import Task

scholarly_labels = ScholarlyArticleLabels()
tasks = [
    Task(
        label="Add main subject to scholarly articles",
        question="Is this a valid subject for this article?",
        labels=scholarly_labels
    )
]