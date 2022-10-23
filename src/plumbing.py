import os
import zlib
from datetime import date
from hashlib import sha1
from typing import List

from src.index import IndexEntry, parse_index_entries_to_dict, read_entries
from src.repository import find_repository

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
    assert len(sha) == 40
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


def hash_object(object_type, path=None, data=None, write=True) -> str:
    if object_type == "blob":
        with open(path, "rb") as file:  # type: ignore
            data = file.read()
            return hash_object_data(object_type, data, write)
    else:
        return hash_object_data(object_type, data, write)


def hash_object_data(object_type, data, write) -> str:
    repo = None
    object_type = object_type.encode("ascii")

    obj_class = object_class(object_type)
    obj = obj_class(repo, data)

    length = len(obj.data)
    header = obj.object_type + b" " + str(length).encode("ascii") + b"\0"
    full_data = header + obj.serialize()
    sha: str = sha1(full_data).hexdigest()

    assert len(sha) == 40

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


def ls_tree(tree_ish) -> List:
    repo = find_repository()
    object_ref = find_object(repo, tree_ish, object_type=b"tree")
    obj: Tree = read_object(repo, object_ref)

    items = []
    for item in obj.items:
        mode = "0" * (6 - len(item.mode)) + item.mode.decode("ascii")
        type = read_object(repo, item.sha).object_type.decode("ascii")
        items.append((mode, type, item.sha, item.path.decode("ascii")))

    return items


def write_tree() -> str:
    """
    Create recursively a tree object from the index
    """
    entries = read_entries()
    parsed_entries = parse_index_entries_to_dict(entries)
    sha = hash_tree_recursive(parsed_entries)
    return sha


def write_commit(tree_sha, message, parents=[]):
    data = b"tree " + tree_sha.encode("ascii") + b"\n"
    for parent in parents:
        data += b"parent " + parent.encode("ascii") + b"\n"

    # seconds since 1970
    date_seconds = str(int(date.today().strftime("%s"))).encode("ascii")
    date_timezone = b"+0000"
    data += (
        b"author pepito <pepito@calp.com> "
        + date_seconds
        + b" "
        + date_timezone
        + b"\n"
    )
    data += (
        b"committer pepito <pepito@calp.com> "
        + date_seconds
        + b" "
        + date_timezone
        + b"\n"
    )
    data += b"\n" + message.encode("ascii")

    commit_sha1 = hash_object("commit", data=data, write=True)
    return commit_sha1


def hash_tree_recursive(entries: dict) -> str:
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
            sha_child = hash_tree_recursive(item)
            mode = b"40000"
            path = entry.encode("ascii")
            data += mode + b" " + path + b"\x00" + bytes.fromhex(sha_child)
        else:
            # Is a file
            data += (
                b"100644" + b" " + entry.encode("ascii") + b"\x00" + bytes.fromhex(item)
            )
    sha = hash_object("tree", data=data, write=True)
    return sha


def get_reference(ref):
    """
    Get the branch name or HEAD, and return the commit sha
    cases:
        HEAD: {commit-sha-1} o 'ref: refs/heads/main'
    """
    repo = find_repository()
    path = repo.build_path(ref)
    if not os.path.exists(path):
        return None

    with open(repo.build_path(ref), "r") as file:
        data = file.read().strip()

    if data.startswith("ref: "):
        return get_reference(data[5:])
    else:
        return data


def get_commit(commit_ref):
    # commit_ref: sha1 of commit | branch_name
    repo = find_repository()
    path = repo.build_path(["refs", "heads", commit_ref])
    if os.path.exists(path):
        with open(path, "r") as file:
            commit_ref = file.read().strip()

    return read_object(repo, commit_ref)


def get_current_commit():
    current_commit_ref = get_reference("HEAD")
    return get_commit(current_commit_ref)


def update_current_ref(sha):
    repo = find_repository()
    with open(repo.build_path("HEAD"), "r") as file:
        head_data = file.read().strip()

    if head_data.startswith("ref: "):
        ref = head_data[5:]
        with open(repo.build_path(ref), "w") as file:
            file.write(sha)
    else:
        with open(repo.build_path("HEAD"), "w") as file:
            file.write(sha)


def get_index_entries_from_commit(commit_sha) -> List[IndexEntry]:
    repo = find_repository()
    commit = read_object(repo, commit_sha)
    tree_sha = commit.commit_data[b"tree"].decode("ascii")

    tree_items = ls_tree(tree_sha)
    return get_index_entries_rec(tree_items)


def get_index_entries_rec(tree_items: List, seed_path=[]) -> List[IndexEntry]:
    entries = []
    for mode, type, sha, path in tree_items:
        if type == "tree":
            assert len(sha) == 40
            entries += get_index_entries_rec(ls_tree(sha), seed_path + [path])
        else:
            # TODO: agregar mode a index entry?
            path = "/".join(seed_path + [path])
            entries.append(IndexEntry(path, sha))
    return entries


# def get_commit_changes(commit_sha):
#     """
#     Get the changes from a commit
#     """
#     repo = find_repository()
#     commit = read_object(repo, commit_sha)
#     current_tree_sha1 = commit.commit_data[b"tree"].decode("ascii")

#     parent_commit = commit.commit_data.get(b"parent", None)

#     tree = ls_tree(current_tree_sha1)
#     differences = set(tree)
#     if parent_commit:
#         parent_commit_sha1 = parent_commit.decode("ascii")
#         parent_commit = read_object(repo, parent_commit_sha1)
#         parent_tree_sha1 = parent_commit.commit_data[b"tree"].decode("ascii")
#         differences -= set(ls_tree(parent_tree_sha1))

#     return differences


def get_commit_changes(commit_sha):
    """
    Get the changes from a commit
    """
    repo = find_repository()
    commit = read_object(repo, commit_sha)
    index_entries = get_index_entries_from_commit(commit_sha)
    differences = {
        (index_entry.path, index_entry.hash) for index_entry in index_entries
    }

    parent_commit = commit.commit_data.get(b"parent", None)
    if parent_commit:
        parent_commit_sha1 = parent_commit.decode("ascii")
        parent_commit = read_object(repo, parent_commit_sha1)

        parent_entries = get_index_entries_from_commit(parent_commit_sha1)
        differences -= {
            (index_entry.path, index_entry.hash) for index_entry in parent_entries
        }
    return differences
