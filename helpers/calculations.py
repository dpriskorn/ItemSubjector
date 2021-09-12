import random

import config


def calculate_random_offset():
    # Calculate offset between 0 and
    config.random_offset = random.randint(0, 10000)