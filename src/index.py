import os
from typing import List

from src.repository import find_repository


class IndexEntry:
    # {hash} {path}\n
    def __init__(self, path, hash):
        self.path = path
        self.hash = hash


def read_entries() -> List[IndexEntry]:
    entries = []
    repository = find_repository()
    index_path = repository.build_path("index")

    assert index_path.startswith(repository.gitdir)
    if not os.path.exists(index_path):
        return entries

    with open(index_path, "rb") as file:
        # Instantiate IndexEntry objects
        data: str = file.read().decode("ascii")
        for line in data.splitlines():
            hash, path = line.split(" ")
            entries.append(IndexEntry(path, hash))

    return entries


def write_entries(entries: List[IndexEntry]):
    # TODO: Sort entires by path

    entries = sorted(entries, key=lambda entry: entry.path)

    data = b""
    for entry in entries:
        data += f"{entry.hash} {entry.path}\n".encode("ascii")

    repository = find_repository()
    index_path = repository.build_path("index")
    with open(index_path, "wb") as file:
        file.write(data)
