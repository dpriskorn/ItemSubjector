import logging
from typing import TYPE_CHECKING, List, Optional, Set
from urllib.parse import quote

from wikibaseintegrator import WikibaseIntegrator  # type: ignore
from wikibaseintegrator.datatypes import Item as ItemType  # type: ignore
from wikibaseintegrator.models import Claim  # type: ignore
from wikibaseintegrator.wbi_helpers import search_entities  # type: ignore

import config
from src.helpers.calculations import calculate_random_editgroups_hash
from src.helpers.cleaning import clean_rich_formatting
from src.helpers.console import console
from src.helpers.questions import ask_yes_no_question
from src.models.items import Items
from src.models.items.riksdagen_documents import RiksdagenDocumentItems
from src.models.items.scholarly_articles import ScholarlyArticleItems
from src.models.wikimedia.wikidata.enums import Property, Qid
from src.models.wikimedia.wikidata.item import Item
from src.tasks import TaskIds

if TYPE_CHECKING:
    from src.models.batch_job import BatchJob

logger = logging.getLogger(__name__)


class MainSubjectItem(Item):
    search_strings: Set[str] = set()
    items: Optional[Items] = None
    number_of_queries: int = 0

    class Config:
        arbitrary_types_allowed = True

    def __alias_appears_in_label_of_a_qid__(self, alias: str) -> bool:
        if not alias:
            raise ValueError("alias was none")
        results = search_entities(alias, dict_result=True)
        for result in results:
            if result["label"] == alias:
                qid = result["id"]
                logger.info(f"Found {alias} as label in {qid}")
                # verify that it is not a scientific article
                return self.__is_not_scientific_article__(qid=qid)
        return False

    @staticmethod
    def __is_not_scientific_article__(qid: str):
        """Looks up the QID in Wikidata to check whether it is a scholarly article or not.
        We negate the result"""
        # TODO avoid negating here
        if not qid:
            raise ValueError("qid was None")
        wbi = WikibaseIntegrator()
        item = wbi.item.get(qid)
        claims: List[Claim] = item.claims
        for claim in claims:
            if claim.mainsnak.property_number == Property.INSTANCE_OF.value:
                qid = claim.mainsnak.datavalue["value"]["id"]
                logger.info(f"Found P31 with value {qid}")
                # console.print(claim.mainsnak)
                if qid == Qid.SCHOLARLY_ARTICLE.value:
                    logger.debug("__is_not_scientific_article__:returning false now")
                    return False
                else:
                    return True

    def __str__(self):
        """Return label and description, the latter cut to 50 chars"""
        string = (
            f"label: [bold]{clean_rich_formatting(self.label)}[/bold]\n"
            f"aliases: {', '.join(self.aliases)}\n"
            f"description: {self.description[:70]}\n"
            f"{self.url}\n"
        )
        for url in self.search_urls():
            string = string + f"{url}\n"
        return string

    def add_to_items(self, jobs: List["BatchJob"] = None, job_count: int = None):
        """Add a suggested Qid as main subject on all items that
        have a label that matches one of the search strings for this Qid
        We calculate a new edit group hash each time this function is
        called so similar edits are grouped and easily be undone.

        This function is non-interactive"""
        if not self.items:
            raise ValueError("Items was None")
        if not self.items.sparql_items:
            raise ValueError("items.sparql_items was None")
        if not jobs:
            raise ValueError("jobs was None")
        if not job_count:
            raise ValueError("job count was None")
        editgroups_hash: str = calculate_random_editgroups_hash()
        count = 0
        for target_item in self.items.sparql_items:
            count += 1
            if not target_item.label:
                target_item.label = "main_subject_item with missing label"
            with console.status(
                f"Uploading main subject "
                f"[green]{clean_rich_formatting(self.label)}[/green] "
                f"to {clean_rich_formatting(target_item.label)} ({target_item.id})"
            ):
                main_subject_property = "P921"
                reference = ItemType(
                    "Q69652283",  # inferred from title
                    prop_nr="P887",  # based on heuristic
                )
                statement = ItemType(
                    self.id,
                    prop_nr=main_subject_property,
                    references=[reference],
                )
                target_item.upload_one_statement_to_wikidata(
                    statement=statement,
                    summary=f"[[Property:{main_subject_property}]]: [[{self.id}]]",
                    editgroups_hash=editgroups_hash,
                )
            console.print(
                f"(job {job_count}/{len(jobs)})(main_subject_item {count}/{self.items.number_of_sparql_items} "
                f"Added '{clean_rich_formatting(self.label)}' to "
                f"{clean_rich_formatting(target_item.label)}: {target_item.url}"
            )
            # input("Press enter to continue")

    @staticmethod
    def __clean_special_symbols__(string: str):
        return string.replace("®", "").replace("™", "").replace('"', "")

    def __extract_search_strings__(self):
        if not self.args:
            raise ValueError("args was None")
        else:
            logger.debug(f"args:{self.args}")
            if self.args.no_aliases is True:
                console.print("Alias matching is turned off")
                no_aliases = True
            elif self.id in config.no_alias_for_scholarly_items:
                logger.info(
                    f"Alias matching is turned off for this main_subject_item: {self.label}"
                )
                no_aliases = True
            else:
                no_aliases = False
        if not self.label:
            raise ValueError("self.label was None")
        self.search_strings: Set[str] = set()
        self.search_strings.add(self.__clean_special_symbols__(self.label))
        if self.aliases and no_aliases is False:
            for alias in self.aliases:
                # logger.debug(f"extracting alias:{alias}")
                if len(alias) < 5 and alias not in config.list_of_allowed_aliases:
                    console.print(
                        f"Skipping short alias '{alias}' to avoid false positives",
                        style="#FF8000",
                    )
                elif self.__alias_appears_in_label_of_a_qid__(alias=alias):
                    console.print(
                        f"Skipped '{alias}' because it appears "
                        f"in a label of at least one Qid that is not a scholarly article",
                        style="#FF8000",
                    )
                elif alias in config.list_of_allowed_aliases:
                    console.print(f"Found {alias} in the allow sparql_items")
                    self.search_strings.add(self.__clean_special_symbols__(alias))
                else:
                    self.search_strings.add(self.__clean_special_symbols__(alias))

    def print_search_strings(self):
        # logger.debug(f"search_strings:{self.search_strings}")
        from src.helpers.cli_messages import print_search_strings_table

        print_search_strings_table(args=self.args, search_strings=self.search_strings)

    def search_urls(self) -> List[str]:
        if not self.search_strings:
            raise ValueError("self.search_strings was None")
        urls = []
        for search_string in self.search_strings:
            search_term = quote(f'"{search_string}"')
            urls.append(f"https://www.wikidata.org/w/index.php?search={search_term}")
        return urls

    def __prepare_before_fetching_items__(self):
        self.__extract_search_strings__()
        self.__check_we_got_what_we_need__()
        if config.loglevel in [logging.INFO, logging.DEBUG]:
            self.print_search_strings()
        self.__count_number_of_queries__()
        self.__instantiate_the_right_class_for_this_task__()

    def __parse_into_job__(self):
        if self.items.number_of_sparql_items:
            self.items.remove_duplicates()
            self.items.random_shuffle_items()
            from src import BatchJob

            job = BatchJob(
                number_of_queries=self.number_of_queries,
                main_subject_item=self,
            )
            return job
        else:
            console.print("No matching items found")
            return None

    def __count_number_of_queries__(self):
        self.number_of_queries = (
            len(self.search_strings) * self.task.number_of_queries_per_search_string
        )

    def __check_we_got_what_we_need__(self):
        if not self.search_strings:
            raise ValueError("search_strings was None")
        if not self.task:
            raise ValueError("task was None")

    def __instantiate_the_right_class_for_this_task__(self):
        if self.task.id == TaskIds.SCHOLARLY_ARTICLES:
            self.items = ScholarlyArticleItems(main_subject_item=self)
        elif self.task.id == TaskIds.RIKSDAGEN_DOCUMENTS:
            self.items = RiksdagenDocumentItems(main_subject_item=self)
        # elif self.task.id == TaskIds.THESIS:
        #     items = ThesisItems(main_subject_item=self)
        # elif self.task.id == TaskIds.ACADEMIC_JOURNALS:
        #     items = AcademicJournalItems(main_subject_item=self)
        else:
            raise ValueError(f"{self.task.id} was not recognized")

    def fetch_items_and_get_job_if_confirmed(self) -> Optional["BatchJob"]:
        """This method handles all the work needed to return a job"""
        self.__strip_qid_prefix__()
        self.__fetch_label_and_description_and_aliases__()
        if self.__got_label__():
            console.print(f"Working on {self.label}")
            if self.__is_confirmed__():
                return self.__fetch_and_parse__()
        return None

    def __is_confirmed__(self) -> bool:
        if self.confirmation:
            return ask_yes_no_question("Do you want to continue?")
        else:
            return True

    def __fetch_and_parse__(self) -> Optional["BatchJob"]:
        self.__prepare_before_fetching_items__()
        if self.items:
            with console.status(
                f"Fetching items with labels that have one of "
                f"the search strings by running a total of "
                f"{self.number_of_queries} "
                f"queries on WDQS..."
            ):
                self.items.fetch_based_on_label()
            return self.__parse_into_job__()
        else:
            raise ValueError("items was None")

    def __got_label__(self) -> bool:
        if not self.label:
            if not self.task:
                raise ValueError("task was None")
            console.print(
                f"Label for {self.task.language_code.name.title()} was None, see {self.url}, skipping"
            )
            return False
        else:
            return True
