import collections
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
        if not self.commit_data:
            return

        raw = b''
        for key, value in self.commit_data.items():
            if key == b'':
                continue

            if not isinstance(value, list):
                value = [value]

            for v in value:
                raw += key + b' ' + (v.replace(b'\n', b'\n ')) + b'\n'

        raw += b'\n' + self.commit_data[b'']
        return raw

    def deserialize(self, data):
        self.commit_data = parse_commit(data)
        # from pprint import pprint
        # pprint(dict(self.commit_data))


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
    with open(path, 'rb') as file:
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


def parse_commit(raw, start=0, commit_data=None):
    """
    """
    if not commit_data:
        commit_data = collections.OrderedDict()

    space = raw.find(b' ', start)
    new_line = raw.find(b'\n', start)

    # If newline appears first (or there's no space at all, in which
    # case find returns -1), we assume a blank line.  A blank line
    # means the remainder of the data is the message.
    if (space < 0) or (new_line < space):
        commit_data[b''] = raw[start + 1:]
        return commit_data

    key = raw[start:space]
    end = start
    while True:
        end = raw.find(b'\n', end + 1)
        if raw[end + 1] != ord(' '):
            break

    value = raw[space + 1:end]

    if key in commit_data:
        if isinstance(commit_data[key], list):
            commit_data[key].append(value)
        else:
            commit_data[key] = [commit_data[key], value]
    else:
        commit_data[key] = value
    return parse_commit(raw, start=end + 1, commit_data=commit_data)


OBJECT_CLASSES = [Blob, Commit, Tree]

OBJECT_CHOICES = {}
for cls in OBJECT_CLASSES:
    OBJECT_CHOICES[cls.name] = cls


def object_class(name):
    return OBJECT_CHOICES[name]
