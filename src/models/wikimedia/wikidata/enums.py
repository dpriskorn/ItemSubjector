from enum import Enum


class WikidataGrammaticalFeature(Enum):
    ACTIVE_VOICE = "Q1317831"
    DEFINITE = "Q53997851"
    GENITIVE_CASE = "Q146233"
    IMPERATIVE = "Q22716"
    INDEFINITE = "Q53997857"
    INFINITIVE = "Q179230"
    NOMINATIVE_CASE = "Q131105"
    PASSIVE_VOICE = "Q1194697"
    PLURAL = "Q146786"
    PRESENT_TENSE = "Q192613"
    PRETERITE = "Q442485"
    SIMPLE_PRESENT = "Q3910936"
    SINGULAR = "Q110786"
    SUPINE = "Q548470"
    THIRD_PERSON_SINGULAR = "Q51929447"


class WikidataLexicalCategory(Enum):
    ADJECTIVE = "Q34698"
    ADVERB = "Q380057"
    AFFIX = "Q62155"
    NOUN = "Q1084"
    PROPER_NOUN = "Q147276"
    VERB = "Q24905"


class WikidataNamespaceLetters(Enum):
    ITEM = "Q"
    LEXEME = "L"
    PROPERTY = "P"
    # FORM = "F"
    # SENSE = "S"


class Property(Enum):
    INSTANCE_OF = "P31"


class Qid(Enum):
    SCHOLARLY_ARTICLE = "Q13442814"
