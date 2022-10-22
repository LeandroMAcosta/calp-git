import os
from hashlib import shake_256
from typing import List

from src.index import IndexEntry, read_entries, write_entries
from src.plumbing import hash_object, write_tree
from src.repository import GITDIR, create_repository


def init(path):
    create_repository(path)


def add(paths):
    # paths: ["A/1.txt", "2.txt"]
    # Read the entries from the staging area in the index file
    entries: List[IndexEntry] = read_entries()
    entries = [entry for entry in entries if entry.path not in paths]

    for path in paths:
        if path.startswith(GITDIR) or path in [".", ".."]:
            raise Exception(f"Cannot add {path} to the index")

    for path in paths:
        # TODO: Handle directories
        if os.path.exists(path):
            hash = hash_object("blob", path, write=True)
            entry = IndexEntry(path, hash)
            entries.append(entry)

    write_entries(entries)


def commit(message):
    sha = write_tree()
    print(sha)
    # Read the entries from the staging area in the index file
    # entries: List[IndexEntry] = read_entries()
    # parsed_entries = parse_index_to_dict(entries)

    # TODO:
    # tree = hash_object("tree", entries, write=True)
    # parent = None
    # commit = hash_object("commit", (tree, parent, message), write=True)
    # print(f"[{commit}] {message}"
