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
