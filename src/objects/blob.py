from .base import BaseObject


class Blob(BaseObject):
    object_type = b"blob"

    def serialize(self):
        return self.blob_data

    def deserialize(self, data):
        self.blob_data = data
