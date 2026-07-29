from django.contrib.auth.base_user import BaseUserManager
from apps.common.utils.username import generate_username


class UserManager(BaseUserManager):

    def create_user(
        self,
        email,
        first_name,
        last_name,
        password=None,
        **extra_fields
    ):
        
        if not email:
            raise ValueError(
                "Email is required"
            )

        if not first_name or not last_name:
            raise ValueError(
                "First name and last name are required"
            )


        email = self.normalize_email(email)

        username = generate_username(
            self.model,
            first_name,
            last_name
        )

        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        user.set_password(password)

        user.save(
            using=self._db
        )

        return user


    def create_superuser(
        self,
        email,
        first_name,
        last_name,
        password=None,
        **extra_fields
    ):

        extra_fields.setdefault(
            "is_staff",
            True
        )

        extra_fields.setdefault(
            "is_superuser",
            True
        )

        extra_fields.setdefault(
            "is_active",
            True
        )

        extra_fields.setdefault(
            "is_verified",
            True
        )


        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Superuser must have is_staff=True"
            )


        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Superuser must have is_superuser=True"
            )


        return self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            **extra_fields
        )