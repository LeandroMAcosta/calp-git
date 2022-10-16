from src.objects import find_object, object_hash, read_object
from src.repository import Repository, find_repository


def hash_object(type, path, write):
    """ """
    repo = None
    if write:
        repo = Repository(".")

    with open(path, "rb") as file:
        sha = object_hash(file, type.encode("ascii"), repo)
        print(sha)


def cat_file(type, object):
    """ """
    repo = find_repository()
    obj = read_object(repo, find_object(repo, object, type_name=type))
    print(obj.serialize())
