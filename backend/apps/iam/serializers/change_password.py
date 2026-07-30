from django.contrib.auth import password_validation
from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    new_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    def validate_new_password(self, value):

        user = self.context.get("request").user

        password_validation.validate_password(value, user=user)

        return value
