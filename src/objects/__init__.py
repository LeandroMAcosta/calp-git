import zlib
from hashlib import sha1

from .blob import Blob
from .commit import Commit
from .tree import Tree

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


def object_hash(file, type_name, repo=None):
    data = file.read()
    obj_class = object_class(type_name)

    obj = obj_class(repo, data)
    content = obj.serialize()
    length = len(obj.data)
    header = obj.object_type + b" " + str(length).encode("ascii") + b"\0"
    sha = sha1(header + content).hexdigest()

    # if the repository is passed, we save it in the database
    if repo is not None:
        path = repo.create_dir("objects", sha[0:2])
        with open(f"{path}/{sha[2:]}", "wb") as file:
            file.write(zlib.compress(header + content))
    return sha
