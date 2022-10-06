def clean_rich_formatting(label):
    # Fix rich parse bug with "[/TSUP]" and "[/ITAL]"
    return label.replace("[/", "['/")
