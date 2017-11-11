import glob
from os.path import isfile, join


def get_all_files(directory):
    return [filename for filename in glob.iglob(join(directory, '**'), recursive=True) if isfile(filename)]
