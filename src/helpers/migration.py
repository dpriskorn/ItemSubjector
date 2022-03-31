import config


def migrate_pickle_detection():
    try:
        if config.job_pickle_file_path is None:
            raise ValueError(
                "the variable job_pickle_file_path in config "
                "has to contain a string like 'pickle.dat'"
            )
    except AttributeError:
        raise ValueError(
            "You need to migrate the new pickle variables"
            "in __init__.example.py to your __init__.py before "
            "you can continue"
        )
