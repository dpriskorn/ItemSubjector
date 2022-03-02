"""
Settings for items
"""
from typing import List

list_of_allowed_aliases: List[str] = []  # Add elements like this ["API"]

# Scholarly items settings
blocklist_for_scholarly_items: List[str] = [
    "Q28196260",
    "Q27863114",
    "Q28196260",
    "Q28196266",  # iodine
    "Q27863114",  # testosterone
]
no_alias_for_scholarly_items: List[str] = ["Q407541", "Q423930", "Q502327"]
