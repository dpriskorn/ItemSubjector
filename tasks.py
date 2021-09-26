from helpers.enums import SupportedLanguageCode
from models.riksdagen_documents import RiksdagenDocumentItems
from models.scholarly_articles import ScholarlyArticleItems
from models.task import Task

# When adding a new task, also add it in the enum

tasks = [
    Task(
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
        ),
        items=ScholarlyArticleItems(),
        label="Work on main subject on scholarly articles (English)",
        language_code=SupportedLanguageCode.ENGLISH,
        question="Is this a valid subject for this article?",
    ),
    Task(
        best_practice_information=None,
        items=RiksdagenDocumentItems(),
        label="Work on main subject on documents from Riksdagen (Swedish)",
        language_code=SupportedLanguageCode.SWEDISH,
        question="Is this a valid subject for this dissertation?",
    ),
    # Task(
    #     best_practice_information=None,
    #     items=,
    #     label="Add main subject to academic dissertations (English)",
    #     language_code=SupportedLanguageCode.ENGLISH,
    #     question="Is this a valid subject for this document?",
    # )
]
