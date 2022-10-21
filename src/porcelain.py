import os
from typing import List

from src.index import IndexEntry, read_entries, write_entries
from src.plumbing import hash_object
from src.repository import GITDIR, create_repository, find_repository
from src.utils import get_files_rec, print_status_messages

def init(path):
    create_repository(path)


def add(paths):
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

def status():
    # Read the entries from the staging area in the index file
    entries: List[IndexEntry] = read_entries()
    repo = find_repository()
    files = get_files_rec(repo.worktree)
    modified = []
    untracked = []
    deleted = []
    hashes = []

    for file in files:
        hash = hash_object("blob", file, write=False)
        hashes.append(hash)
        found = False

        for entry in entries:
            if entry.hash != hash and entry.path in file:
                modified.append(entry.path)
                found = True
                break
            elif entry.hash == hash and entry.path in file:
                found = True
                break
        
        if not found:
            relative_path = os.path.relpath(file, repo.worktree)
            untracked.append(relative_path)

    for entry in entries:
        if not entry.hash in hashes and entry.path not in modified:
            deleted.append(entry.path)

    print_status_messages(modified, untracked, deleted)



    
