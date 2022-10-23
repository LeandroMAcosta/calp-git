import re


class BaseObject:

    repo = None
    data = None

    def __init__(self, repo, data=None):
        self.repo = repo
        self.data = data

        if data is not None:
            self.deserialize(data)

    def serialize(self):
        raise NotImplementedError

    def deserialize(self, data):
        raise NotImplementedError


def is_sha1(sha1: str) -> bool:
    pattern = re.compile(r'\b[0-9a-fA-F]{40}\b')
    return len(sha1) == 40 and pattern.match(sha1) is not None
