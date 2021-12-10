import uuid
from django.utils.deconstruct import deconstructible


@deconstructible
class UploadPath(object):

    def __init__(self, file_type):
        self.file_type = file_type

    def __call__(self, obj, f):
        ext = f[f.rfind('.'):]
        return f"media/user_{obj.application.user.id}/{self.file_type}{uuid.uuid4()}{ext}"
