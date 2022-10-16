from src.objects import find_object, object_hash, read_object
from src.objects.tree import Tree
from src.repository import Repository, find_repository


def hash_object(type, path, write):
    """ """
    repo = None
    if write:
        repo = Repository(".")

    with open(path, "rb") as file:
        sha = object_hash(file, type.encode("ascii"), repo)
        print(sha)


def cat_file(object_type, object):
    """ """
    repo = find_repository()
    obj = read_object(repo, find_object(repo, object, object_type=object_type))
    # for key, value in obj.de():
    #     print(f"{key}: {value}")
    import ipdb

    ipdb.set_trace()
    res: bytes = obj.serialize()
    print(res.decode("ascii"))


def ls_tree(tree_ish):
    repo = find_repository()
    object_ref = find_object(repo, tree_ish, object_type=b"tree")
    obj: Tree = read_object(repo, object_ref)

    for item in obj.items:
        mode = "0" * (6 - len(item.mode)) + item.mode.decode("ascii")
        type = read_object(repo, item.sha).object_type.decode("ascii")
        print(f"{mode} {type} {item.sha}\t{item.path.decode('ascii')}")
