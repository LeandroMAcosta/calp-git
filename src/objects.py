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


OBJECT_CLASSES = [Blob, Commit, Tree]

OBJECT_CHOICES = {}
for cls in OBJECT_CLASSES:
    OBJECT_CHOICES[cls.name] = cls


def object_class(name):
    return OBJECT_CHOICES[name]
