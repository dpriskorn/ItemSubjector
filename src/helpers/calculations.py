import random


def calculate_random_editgroups_hash():
    return f"{random.randrange(0, 2**48):x}"
