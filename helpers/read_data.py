import os
from typing import List


def get_main_subjects_from_file() -> List[str]:
    # read the data file
    file_path = "data/main_subjects.csv"
    main_subjects_path = f"{os.getcwd()}/{file_path}"
    with open(main_subjects_path) as file:
        lines = file.readlines()
        main_subjects = [line.rstrip() for line in lines]
    return main_subjects