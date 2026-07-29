from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "uuid",
            "email",
            "username",
            "first_name",
            "last_name",
            "display_name",
            "profile_picture",
            "bio",
            "timezone",
            "is_verified",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields