import base64
from django.db.models import CharField
from decouple import config
from cryptography.fernet import Fernet


class EncryptedField(CharField):
    """
    Custom model field to store sensitive data
    """
    def __init__(self, *args, db_collation=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.block_size = 16
        self.cipher = Fernet(base64.urlsafe_b64encode(str.encode(config('SECRET_KEY')[:32])))
    def pad(self, value):
        return value + (self.block_size - len(value) % self.block_size) * chr(
            self.block_size - len(value) % self.block_size
        )
    def unpad(self, value):
        return value[: -ord(value[len(value) - 1:])]
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.unpad(self.cipher.decrypt(bytes(str.encode(value)))).decode()
    def get_prep_value(self, value):
        if value is None:
            return value
        return self.cipher.encrypt(bytes(str.encode(self.pad(value)))).decode()

