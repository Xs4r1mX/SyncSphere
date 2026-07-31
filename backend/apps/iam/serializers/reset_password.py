from rest_framework import serializers

from django.contrib.auth import password_validation


class ResetPasswordSerializer(serializers.Serializer):

    token = serializers.CharField(
        required=True,
        write_only=True,
    )

    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
    )

    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    def validate(self, attrs):
        """
        Validate password confirmation
        and password strength.
        """

        new_password = attrs.get("new_password")

        confirm_password = attrs.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        # Validate password strength
        password_validation.validate_password(new_password)

        return attrs
