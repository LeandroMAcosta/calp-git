from src.objects.sha_object import ShaObject


class Blob(ShaObject):
    object_type = b"blob"

    def serialize(self):
        return self.blob_data

    def deserialize(self, data):
        self.blob_data = data
