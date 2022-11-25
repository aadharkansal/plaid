import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken


class AbstractBaseModel(models.Model):
    """
    Base abstract model, that has `uuid` instead of `id` and includes `created_at`, `updated_at` fields.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(_("Date Created"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("Date Updated"), auto_now=True, db_index=True)

    class Meta:
        abstract = True

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.uuid}>'


class User(AbstractUser, AbstractBaseModel):
    email_verified = models.BooleanField(default=False)
    phone_number = models.TextField(max_length=20, blank=False, null=False)
    phone_number_verified = models.BooleanField(default=False)

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
