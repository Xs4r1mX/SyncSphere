from rest_framework import serializers

from apps.transfers.constants import TransferConflictPolicy, TransferOperation
from apps.transfers.models import TransferItem, TransferJob


class CreateTransferSerializer(serializers.Serializer):
    operation = serializers.ChoiceField(choices=TransferOperation.choices)
    source_connection_uuid = serializers.UUIDField()
    dest_connection_uuid = serializers.UUIDField()
    source_item_id = serializers.CharField(max_length=255, trim_whitespace=True)
    dest_parent_id = serializers.CharField(
        max_length=255,
        required=False,
        default="root",
        trim_whitespace=True,
    )
    conflict_policy = serializers.ChoiceField(
        choices=TransferConflictPolicy.choices,
        required=False,
        default=TransferConflictPolicy.REJECT,
    )

    def validate_source_item_id(self, value: str) -> str:
        if not value.strip():
            raise serializers.ValidationError("source_item_id is required.")
        return value.strip()


class TransferJobSerializer(serializers.ModelSerializer):
    source_connection_uuid = serializers.UUIDField(
        source="source_connection.uuid",
        read_only=True,
    )
    dest_connection_uuid = serializers.UUIDField(
        source="dest_connection.uuid",
        read_only=True,
    )

    class Meta:
        model = TransferJob
        fields = (
            "uuid",
            "operation",
            "conflict_policy",
            "status",
            "source_connection_uuid",
            "dest_connection_uuid",
            "source_item_id",
            "source_item_name",
            "source_is_folder",
            "dest_parent_id",
            "total_bytes",
            "bytes_transferred",
            "items_total",
            "items_completed",
            "items_failed",
            "error_code",
            "error_message",
            "cancel_requested",
            "started_at",
            "finished_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class TransferItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferItem
        fields = (
            "uuid",
            "sequence",
            "kind",
            "source_item_id",
            "source_path",
            "source_name",
            "dest_parent_id",
            "dest_item_id",
            "dest_name",
            "size_bytes",
            "mime_type",
            "status",
            "error_code",
            "error_message",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
