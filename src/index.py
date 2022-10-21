import os
from typing import List

from src.repository import find_repository


class IndexEntry:
    # {hash} {path}\n
    def __init__(self, path, hash):
        self.path = path
        self.hash = hash

    def deserialize(self, data: bytes):
        # TODO: Implement
        ...

    def serialize(self) -> bytes:
        # TODO: Implement
        ...


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


def parse_index_to_dict(entires: List[IndexEntry]) -> dict:
    """
    Build a dict of directories and files from the entries in the index file.

    .git/index
    b729d9500ea4c046f88c4e5c084251ec2cbb64a7 A/B/1.txt
    b729d9500ea4c046f88c4e5c084251ec2cbb6427 A/B/2.txt
    b729d9500ea4c046f88c4e5c084151ec2cbb6427 A/5.txt
    b08f7b08213644cd1609487a660a26cb3edc3813 A/B/3.txt
    f79dfaa021b9972c4a56da87269684e9a73539b5 main.txt

    {
        "A": {
            "5.txt": "b729d9500ea4c046f88c4e5c084151ec2cbb6427",
            "B": {
                "1.txt": "b729d9500ea4c046f88c4e5c084251ec2cbb64a7",
                "2.txt": "b729d9500ea4c046f88c4e5c084251ec2cbb6427",
                "3.txt": "b08f7b08213644cd1609487a660a26cb3edc3813"
            }
        },
        "main.txt": "f79dfaa021b9972c4a56da87269684e9a73539b5"
    }
    """
    dict = {}
    for entry in entires:
        path = entry.path
        if "/" not in path:
            dict[path] = entry.hash
        else:
            dirs = path.split("/")
            parent = dict
            for dir in dirs[:-1]:
                if dir not in parent:
                    parent[dir] = {}
                parent = parent[dir]
            parent[dirs[-1]] = entry.hash
    return dict
