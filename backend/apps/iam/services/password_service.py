from django.contrib.auth.hashers import check_password

from apps.common.exceptions.iam import (
    IncorrectPasswordException,
)


class PasswordService:

    @staticmethod
    def change_password(
        *,
        user,
        old_password,
        new_password,
    ):
        """
        Change password for authenticated user.
        """

        if not check_password(old_password, user.password):

            raise IncorrectPasswordException("Current password is incorrect.")

        if old_password == new_password:

            raise IncorrectPasswordException(
                "New password cannot be same as old password."
            )

        user.set_password(new_password)

        user.save(update_fields=["password"])

        return user
