from enum import Enum


class WikidataGrammaticalFeature(Enum):
    # Swedish
    ACTIVE_VOICE = "Q1317831"
    PRETERITE = "Q442485"
    INFINITIVE = "Q179230"
    PRESENT_TENSE = "Q192613"
    SUPINE = "Q548470"
    IMPERATIVE = "Q22716"
    PASSIVE_VOICE = "Q1194697"
    SINGULAR = "Q110786"
    NOMINATIVE_CASE = "Q131105"
    INDEFINITE = "Q53997857"
    DEFINITE = "Q53997851"
    PLURAL = "Q146786"
    GENITIVE_CASE = "Q146233"
    # English
    SIMPLE_PRESENT = "Q3910936"
    THIRD_PERSON_SINGULAR = "Q51929447"


class WikidataLexicalCategory(Enum):
    NOUN = "Q1084"
    VERB = "Q24905"
    ADVERB = "Q380057"
    ADJECTIVE = "Q34698"
    AFFIX = "Q62155"
    PROPER_NOUN = "Q147276"


class WikimediaLanguageCode(Enum):
    DANISH = "da"
    SWEDISH = "sv"
    BOKMÅL = "nb"
    ENGLISH = "en"
    FRENCH = "fr"
    RUSSIAN = "ru"
    ESTONIAN = "et"
    MALAYALAM = "ml"
    LATIN = "la"
    HEBREW = "he"
    BASQUE = "eu"
    GERMAN = "de"
    BENGALI = "bn"
    CZECH = "cs"


class WikimediaLanguageQID(Enum):
    DANISH = "Q9035"
    SWEDISH = "Q9027"
    BOKMÅL = "Q25167"
    ENGLISH = "Q1860"
    FRENCH = "Q150"
    RUSSIAN = "Q7737"
    ESTONIAN = "Q9072"
    MALAYALAM = "Q36236"
    LATIN = "Q397"
    HEBREW = "Q9288"
    BASQUE = "Q8752"
    GERMAN = "Q188"
    BENGALI = "Q9610"
    CZECH = "Q9056"


class WikidataNamespaceLetters(Enum):
    PROPERTY = "P"
    ITEM = "Q"
    LEXEME = "L"
    # FORM = "F"
    # SENSE = "S"
