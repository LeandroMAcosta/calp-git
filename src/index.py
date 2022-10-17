import os

from src.plumbing import hash_object
from src.repository import Repository


class Entry:
    def __init__(self, path):
        self.path = path
        self.hash = hash_object("blob", path, write=True)


def read_entries():
    entries = []
    index_path = Repository(".").build_path("index")

    if not os.path.exists(index_path):
        return entries

    # TODO: read the index file
    return entries


def write_entries(entries):
    data = b''
    # TODO: build the data

    index_path = Repository(".").build_path("index")
    with open(index_path, "wb") as file:
        file.write(data)
