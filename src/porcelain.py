import os
from typing import List

from src.index import IndexEntry, read_entries, write_entries
from src.plumbing import hash_object
from src.repository import GITDIR, create_repository


def init(path):
    create_repository(path)


def add(paths):
    # Read the entries from the staging area in the index file
    entries: List[IndexEntry] = read_entries()
    entries = [entry for entry in entries if entry.path not in paths]

    for path in paths:
        if path.startswith(GITDIR) or path in [".", ".."]:
            raise Exception(f"Cannot add {path} to the index")

        if os.path.exists(path):
            raise FileExistsError(f"File does not exist: {path}")

    for path in paths:
        # TODO: Handle directories
        hash = hash_object("blob", path, write=True)
        entry = IndexEntry(path, hash)
        entries.append(entry)

    write_entries(entries)
