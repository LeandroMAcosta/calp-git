
import zlib

from src.objects.blob import Blob
from src.objects.commit import Commit
from src.objects.tree import Tree
from src.repository import Repository, find_repository

OBJECT_CLASSES = [Blob, Commit, Tree]
OBJECT_CHOICES = {cls.object_type: cls for cls in OBJECT_CLASSES}


def object_class(object_type):
    try:
        return OBJECT_CHOICES[object_type]
    except KeyError:
        raise TypeError(f"Unknown type {object_type}")


def read_object(repo: Repository, sha):
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


def get_ancestors(repo, commit: Commit):
    """ """
    ancestors = set()
    parents = commit.get_parents()  # sha 1 parents
    for parent in parents:
        parent_commit = read_object(repo, parent)
        ancestors.add(parent_commit)
        ancestors.update(get_ancestors(repo, parent_commit))

    return ancestors


def lca_commit(commit1_ish, commit2_ish):
    """ """
    repo: Repository = find_repository()
    commit1: Commit = read_object(repo, commit1_ish)
    ancestors1 = get_ancestors(repo, commit1)

    commit2: Commit = read_object(repo, commit2_ish)
    while commit2 not in ancestors1:
        # We asume that only has 1 parent
        # Check get_parents doc.
        commit2 = read_object(repo, commit2.get_parents()[0])

    return commit2
