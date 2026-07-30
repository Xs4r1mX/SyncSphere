from rest_framework import serializers


class RefreshTokenSerializer(serializers.Serializer):

    refresh = serializers.CharField(
        required=True,
        trim_whitespace=True,
    )