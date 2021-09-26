import logging


def strip_bad_chars(string):
    # Note this has to match the cleaning done in the sparql query
    # We lowercase and remove common symbols
    # We replace like this to save CPU cycles see
    # https://stackoverflow.com/questions/3411771/best-way-to-replace-multiple-characters-in-a-string
    return (
        string
        # Needed for matching backslashes e.g. "Dmel\CG5330" on Q29717230
        .replace("\\", "\\\\")
        # Needed for when labels contain apostrophe
        .replace("'", "\\'")
        .replace(",", "")
        .replace(":", "")
        .replace(";", "")
        .replace("(", "")
        .replace(")", "")
        .replace("[", "")
        .replace("]", "")
    )


def strip_prefix(qid: str) -> str:
    logger = logging.getLogger(__name__)
    if "https://www.wikidata.org/wiki/" in qid:
        qid = qid[30:]
    if "http://www.wikidata.org/entity/" in qid:
        qid = qid[31:]
    logger.debug(f"qid:{qid}")
    return qid
