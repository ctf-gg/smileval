import os

def initalize_session_persistence(directory = None):
    if not directory:
        directory = os.getcwd()

    experiments_dir = os.path.join(directory, "experiments")
    data_dir = os.path.join(directory, "data")
    # TODO: error handle these?
    if not os.path.isdir(experiments_dir):
        os.mkdir(experiments_dir)
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)