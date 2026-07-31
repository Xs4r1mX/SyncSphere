from rest_framework import serializers


class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField(
        required=True,
        trim_whitespace=True,
    )
