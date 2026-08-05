from rest_framework import serializers

from apps.cloud.models import CloudConnection
from apps.common.constants import ConnectionStatus, ProviderType


class CloudConnectionSerializer(serializers.ModelSerializer):
    provider_label = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()
    has_credentials = serializers.BooleanField(read_only=True)

    class Meta:
        model = CloudConnection
        fields = (
            "uuid",
            "provider",
            "provider_label",
            "display_name",
            "provider_account_id",
            "account_email",
            "status",
            "status_label",
            "scopes",
            "quota_total_bytes",
            "quota_used_bytes",
            "has_credentials",
            "last_synced_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_provider_label(self, obj: CloudConnection) -> str:
        try:
            return ProviderType(obj.provider).label
        except ValueError:
            return obj.provider

    def get_status_label(self, obj: CloudConnection) -> str:
        try:
            return ConnectionStatus(obj.status).label
        except ValueError:
            return obj.status


class UpdateConnectionSerializer(serializers.Serializer):
    display_name = serializers.CharField(max_length=150, trim_whitespace=True)

    def validate_display_name(self, value: str) -> str:
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Display name cannot be empty.")
        return value
