import random


def calculate_random_editgroups_hash():
    return "{:x}".format(random.randrange(0, 2 ** 48))
