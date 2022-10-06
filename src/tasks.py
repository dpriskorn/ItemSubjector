from src.helpers.enums import SupportedLanguageCode, TaskIds
from src.models.task import Task

# When adding a new task, also add it in the enum

tasks = [
    Task(
        **dict(
            id=TaskIds.SCHOLARLY_ARTICLES,
            label="Add main subject to scholarly articles, thesis' and preprints",
            language_code=SupportedLanguageCode.ENGLISH,
            best_practice_information=(
                "When adding Qid main subjects please try to first "
                "educate yourself about the subarea of science a little "
                "and find/create items as specific as possible.\n"
                "E.g. when searching for 'cancer screening' in Wikidata "
                "we find 'gastric cancer screening' in labels of "
                "scientific articles but there is "
                "perhaps no main_subject_item for this yet.\n"
                "In this case it is preferred to first create that main_subject_item "
                "(done in Q108532542 and add that as main subject and "
                "avoid the more general 'cancer screening' until all "
                "sub forms of screening have been matched."
            ),
            number_of_queries_per_search_string=2,
        )
    ),
    Task(
        **dict(
            id=TaskIds.RIKSDAGEN_DOCUMENTS,
            label="Add main subject to documents from Riksdagen",
            language_code=SupportedLanguageCode.SWEDISH,
            best_practice_information=None,
        )
    ),
    # Task(
    #     **dict(
    #         id=TaskIds.THESIS,
    #         label="Add main subject to thesis' and technical reports",
    #         language_code=SupportedLanguageCode.ENGLISH,
    #         best_practice_information=(
    #             "When adding Qid main subjects please try to first "
    #             "educate yourself about the subarea of science a little "
    #             "and find/create items as specific as possible.\n"
    #             "E.g. when searching for 'cancer screening' in Wikidata "
    #             "we find 'gastric cancer screening' in labels of "
    #             "scientific articles but there is "
    #             "perhaps no main_subject_item for this yet.\n"
    #             "In this case it is preferred to first create that main_subject_item "
    #             "(done in Q108532542 and add that as main subject and "
    #             "avoid the more general 'cancer screening' until all "
    #             "sub forms of screening have been matched."
    #         ),
    #     )
    # ),
    # Task(
    #     **dict(
    #         id=TaskIds.ACADEMIC_JOURNALS,
    #         label="Add main subject to academic journals",
    #         language_code=SupportedLanguageCode.ENGLISH,
    #         best_practice_information=None,
    #     )
    # ),
]
