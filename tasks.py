from helpers.enums import SupportedLanguageCode, TaskIds
from models.task import Task

# When adding a new task, also add it in the enum

tasks = [
    Task(
        id=TaskIds.SCHOLARLY_ARTICLES,
        label="Add main subject to scholarly articles",
        question="Is this a valid subject for this article?",
        language_code=SupportedLanguageCode.ENGLISH,
        best_practice_information=(
            "When adding QID main subjects please try to first "
            "educate yourself about the subarea of science a little "
            "and find/create items as specific as possible.\n"
            "E.g. when searching for 'cancer screening' in Wikidata "
            "we find 'gastric cancer screening' in labels of "
            "scientific articles but there is "
            "perhaps no item for this yet.\n"
            "In this case it is preferred to first create that item "
            "(done in Q108532542 and add that as main subject and "
            "avoid the more general 'cancer screening' until all "
            "sub forms of screening have been matched."
        )
    ),
    Task(
        id=TaskIds.RIKSDAGEN_DOCUMENTS,
        label="Add main subject to documents from Riksdagen",
        question="Is this a valid subject for this document?",
        language_code=SupportedLanguageCode.SWEDISH,
        best_practice_information=None
    )
]
