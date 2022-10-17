from src.index import Entry, read_entries, write_entries
from src.repository import create_repository


def init(path):
    create_repository(path)


def add(paths):
    entries = read_entries()

    for path in paths:
        entry = Entry(path)
        entries.append(entry)

    write_entries(entries)
