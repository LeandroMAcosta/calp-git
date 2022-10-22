import os
import zlib
from hashlib import sha1
from typing import List

from src.index import IndexEntry, parse_index_entries_to_dict, read_entries
from src.repository import Repository, find_repository

from .objects.blob import Blob
from .objects.commit import Commit
from .objects.tree import Tree

OBJECT_CLASSES = [Blob, Commit, Tree]
OBJECT_CHOICES = {cls.object_type: cls for cls in OBJECT_CLASSES}


def object_class(object_type):
    try:
        return OBJECT_CHOICES[object_type]
    except KeyError:
        raise TypeError(f"Unknown type {object_type}")


def read_object(repo, sha):
    """ """
    path = repo.build_path("objects", sha[0:2], sha[2:])
    with open(path, "rb") as file:
        raw = zlib.decompress(file.read())
        # Read object type
        type_end = raw.find(b" ")
        type_name = raw[0:type_end]

        # Read and validate object size
        header_end = raw.find(b"\0", type_end)
        size = int(raw[type_end:header_end].decode("ascii"))
        if size != len(raw) - header_end - 1:
            raise Exception(f"Invalid object {sha}: bad length")

        obj_class = object_class(type_name)
        return obj_class(repo, raw[header_end + 1 :])


def find_object(repo, ref, object_type=None) -> str:
    """ """
    # At the moment we only search with the complete hash
    return ref


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
            repo = find_repository()
            path = repo.create_dir("objects", sha[0:2])
            with open(f"{path}/{sha[2:]}", "wb") as file:
                file.write(zlib.compress(full_data))
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


def write_tree():
    entries = read_entries()
    parsed_entries = parse_index_entries_to_dict(entries)
    sha = hash_tree_recurisve(parsed_entries)
    return sha


def hash_tree_recurisve(entries: dict):
    """
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
    data = b""
    for entry, item in entries.items():
        if isinstance(item, dict):
            # Is a directory
            sha_child = hash_tree_recurisve(item)
            mode = b"40000"
            path = entry.encode("ascii")
            data += mode + b" " + path + b"\0" + sha_child
        else:
            # Is a file
            mode = b"100644"
            path = entry.encode("ascii")
            data += mode + b" " + path + b"\0" + item

    sha = hash_object(b"tree", data, True)
    return sha
