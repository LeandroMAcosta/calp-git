import zlib
from hashlib import sha1


class ShaFile:

    def __init__(self, repo, data=None):
        self.repo = repo
        self.data = data

        if data is not None:
            self.deserialize(data)

    def serialize(self):
        raise NotImplementedError

    def deserialize(self, data):
        raise NotImplementedError


class Blob(ShaFile):
    name = b'blob'

    def serialize(self):
        return self.blob_data

    def deserialize(self, data):
        self.blob_data = data


class Commit(ShaFile):
    name = b'commit'

    def serialize(self):
        ...

    def deserialize(self, data):
        ...


class Tree(ShaFile):
    name = b'tree'

    def serialize(self):
        ...

    def deserialize(self, data):
        ...


def read_object(repo, sha):
    """
    """
    path = repo.build_path('objects', sha[0:2], sha[2:])
    with open (path, 'rb') as file:
        raw = zlib.decompress(file.read())
        # Read object type
        type_end = raw.find(b' ')
        type_name = raw[0:type_end]

        # Read and validate object size
        header_end = raw.find(b'\0', type_end)
        size = int(raw[type_end:header_end].decode("ascii"))
        if size != len(raw) - header_end - 1:
            raise Exception(f'Invalid object {sha}: bad length')

        try:
            obj_class = object_class(type_name)
        except KeyError:
            raise TypeError(f'Unknown type {type_name}')

        return obj_class(repo, raw[header_end + 1:])


def find_object(repo, ref, type_name):
    """
    """
    # At the moment we only search with the complete hash
    return ref


def object_hash(file, type_name, repo=None):
    data = file.read()
    try:
        obj_class = object_class(type_name)
    except KeyError:
        raise TypeError(f'Unknown type {type_name}')

    obj = obj_class(repo, data)
    content = obj.serialize()
    length = len(obj.data)
    header = obj.name + b' ' + str(length).encode('ascii') + b'\0'
    sha = sha1(header + content).hexdigest()

    # if the repository is passed, we save it in the database
    if repo is not None:
        path = repo.create_dir('objects', sha[0:2])
        with open(f'{path}/{sha[2:]}', 'wb') as file:
            file.write(zlib.compress(header + content))
    return sha


OBJECT_CLASSES = [Blob, Commit, Tree]

OBJECT_CHOICES = {}
for cls in OBJECT_CLASSES:
    OBJECT_CHOICES[cls.name] = cls


def object_class(name):
    return OBJECT_CHOICES[name]
