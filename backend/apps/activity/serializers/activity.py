from rest_framework import serializers

from apps.activity.constants import ActivityAction, ActivityResourceType
from apps.activity.models import ActivityLog
from apps.activity.services.activity_service import DEFAULT_PAGE_LIMIT, MAX_PAGE_LIMIT


class ActivityLogSerializer(serializers.ModelSerializer):
    connection_uuid = serializers.UUIDField(
        source="connection.uuid",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = ActivityLog
        fields = (
            "uuid",
            "action",
            "resource_type",
            "resource_id",
            "resource_name",
            "connection_uuid",
            "provider",
            "status",
            "metadata",
            "request_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class ActivityListQuerySerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=ActivityAction.choices,
        required=False,
    )
    resource_type = serializers.ChoiceField(
        choices=ActivityResourceType.choices,
        required=False,
    )
    connection_uuid = serializers.UUIDField(required=False)
    provider = serializers.CharField(required=False, max_length=64)
    created_after = serializers.DateTimeField(required=False)
    created_before = serializers.DateTimeField(required=False)
    limit = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=MAX_PAGE_LIMIT,
        default=DEFAULT_PAGE_LIMIT,
    )
    offset = serializers.IntegerField(required=False, min_value=0, default=0)
