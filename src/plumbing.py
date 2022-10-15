import zlib
from hashlib import sha1

from src.objects import object_class
from src.repository import Repository


def hash_object(type, path, write):
    repo = None
    if write:
        repo = Repository('.')

    with open(path, 'rb') as file:
        sha = object_hash(file, type.encode('ascii'), repo)
        print(sha)


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
        path = repo.create_dir('objects', sha[0:2], sha[2:])
        with open(path, 'wb') as file:
            file.write(zlib.compress(header + content))
    return sha
