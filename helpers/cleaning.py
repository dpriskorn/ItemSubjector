def strip_bad_chars(string):
    # Note this has to match the cleaning done in the sparql query
    # We lowercase and remove common symbols
    # We replace like this to save CPU cycles see
    # https://stackoverflow.com/questions/3411771/best-way-to-replace-multiple-characters-in-a-string
    return (
        string
        # Needed for when labels contain apostrophes
        .replace("'", "\\'")
        # Needed for matching backslashes e.g. "Dmel\CG5330" on Q29717230
        .replace("\\", "\\\\")
        .replace(",", "")
        .replace(":", "")
        .replace(";", "")
        .replace("(", "")
        .replace(")", "")
        .replace("[", "")
        .replace("]", "")
    )
