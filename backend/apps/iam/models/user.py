from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin
)

from django.db import models

from apps.common.models import BaseModel

from .managers import UserManager


class User(
    BaseModel,
    AbstractBaseUser,
    PermissionsMixin
):

    email = models.EmailField(
        unique=True,
        db_index=True
    )

    username = models.SlugField(
        max_length=50,
        unique=True,
        db_index=True
    )

    first_name = models.CharField(
        max_length=100,
    )

    last_name = models.CharField(
        max_length=100,
    )

    display_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )


    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True
    )


    bio = models.TextField(
        blank=True
    )


    timezone = models.CharField(
        max_length=50,
        default="UTC"
    )


    is_verified = models.BooleanField(
        default=False
    )


    is_active = models.BooleanField(
        default=True
    )


    is_staff = models.BooleanField(
        default=False
    )


    objects = UserManager()


    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
    ]


    class Meta:
        db_table = "users"


    def __str__(self):
        return self.email


    @property
    def public_name(self):
        """
        Returns display name fallback.
        """

        if self.display_name:
            return self.display_name

        full_name = (
            f"{self.first_name} {self.last_name}"
        ).strip()

        return full_name or self.username