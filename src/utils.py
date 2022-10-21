import os
from src.repository import GITDIR

def get_files_rec(directory):
    files = []
    for path in os.scandir(directory):
        if not path.name.startswith(GITDIR):
            if path.is_file():
                files.append(os.path.join(directory, path))
            else:
                get_files_rec(os.path.join(directory, path))

    return files