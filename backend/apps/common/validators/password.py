import re

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator,
)


class PasswordValidator:
    """
    Custom password validator for application-wide
    password security rules.
    """

    def validate(self, password, user=None):

        errors = []

        # Minimum length
        if len(password) < 8:

            errors.append("Password must be at least 8 characters long.")

        # Lowercase character
        if not re.search(r"[a-z]", password):

            errors.append("Password must contain at least one lowercase letter.")

        # Uppercase character
        if not re.search(r"[A-Z]", password):

            errors.append("Password must contain at least one uppercase letter.")

        # Digit
        if not re.search(r"\d", password):

            errors.append("Password must contain at least one digit.")

        # Special symbol
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\]", password):

            errors.append("Password must contain at least one special character.")

        # Similarity check
        if user:

            similarity_validator = UserAttributeSimilarityValidator()

            try:

                similarity_validator.validate(password, user)

            except ValidationError as error:

                errors.extend(error.messages)

        if errors:

            raise ValidationError(errors)

    def get_help_text(self):

        return (
            "Password must contain at least "
            "8 characters, including uppercase, "
            "lowercase, digit and special character."
        )
