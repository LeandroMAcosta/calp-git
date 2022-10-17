import zlib
from hashlib import sha1

from src.objects import find_object, object_class, read_object
from src.objects.tree import Tree
from src.repository import Repository, find_repository


def hash_object(type, path, write):
    """ """
    repo = None
    object_type = type.encode("ascii")
    with open(path, "rb") as file:
        data = file.read()
        obj_class = object_class(object_type)
        obj = obj_class(repo, data)

        length = len(obj.data)
        header = obj.object_type + b" " + str(length).encode("ascii") + b"\0"
        full_data = header + obj.serialize()
        sha = sha1(full_data).hexdigest()

        if write:
            repo = Repository(".")
            path = repo.create_dir("objects", sha[0:2])
            with open(f"{path}/{sha[2:]}", "wb") as file:
                file.write(zlib.compress(full_data))
    print(sha)
    return sha


def cat_file(object_type, object):
    """ """
    repo = find_repository()
    obj = read_object(repo, find_object(repo, object, object_type=object_type))
    # for key, value in obj.de():
    #     print(f"{key}: {value}")
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
