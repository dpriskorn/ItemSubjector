import config


def migrate_pickle_detection():
    try:
        if config.pickle_file is None:
            raise ValueError("the variable pickle_file in config "
                             "has to contain a string like 'pickle.dat'")
    except AttributeError:
        raise ValueError("You need to migrate the new variable 'pickle_file'"
                         "in config.example.py to your config.py before "
                         "you can continue")
