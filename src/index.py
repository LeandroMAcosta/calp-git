import os
from typing import List

from src.repository import find_repository


class IndexEntry:
    # {hash} {path}\n
    def __init__(self, path, hash):
        self.path = path
        self.hash = hash

    def deserialize(self, data: bytes):
        ...

    # TODO: Implement

    def serialize(self) -> bytes:
        ...

    # TODO: Implement


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
            # TODO: Use deserialize method's in IndexEntry
            hash, path = line.split(" ")
            entries.append(IndexEntry(path, hash))

    return entries


def write_entries(entries: List[IndexEntry]):
    entries = sorted(entries, key=lambda entry: entry.path)

    data = b""
    for entry in entries:
        # TODO: Use serialize method's in IndexEntry
        data += f"{entry.hash} {entry.path}\n".encode("ascii")

    repository = find_repository()
    index_path = repository.build_path("index")
    with open(index_path, "wb") as file:
        file.write(data)
