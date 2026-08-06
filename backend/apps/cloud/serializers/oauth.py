from rest_framework import serializers


class OAuthCallbackSerializer(serializers.Serializer):
    code = serializers.CharField(trim_whitespace=True)
    state = serializers.CharField(trim_whitespace=True)

    def validate_code(self, value: str) -> str:
        if not value:
            raise serializers.ValidationError("Authorization code is required.")
        return value

    def validate_state(self, value: str) -> str:
        if not value:
            raise serializers.ValidationError("OAuth state is required.")
        return value
