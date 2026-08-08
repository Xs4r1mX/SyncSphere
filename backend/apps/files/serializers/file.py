from rest_framework import serializers


class FileItemSerializer(serializers.Serializer):
    provider_item_id = serializers.CharField()
    name = serializers.CharField()
    mime_type = serializers.CharField()
    is_folder = serializers.BooleanField()
    parent_id = serializers.CharField(allow_null=True)
    size = serializers.IntegerField(allow_null=True)
    created_at = serializers.DateTimeField(allow_null=True)
    modified_at = serializers.DateTimeField(allow_null=True)
    trashed = serializers.BooleanField()
    web_view_link = serializers.CharField(allow_null=True)


class FileListSerializer(serializers.Serializer):
    items = FileItemSerializer(many=True)
    next_page_token = serializers.CharField(allow_null=True)


class FileListQuerySerializer(serializers.Serializer):
    parent_id = serializers.CharField(required=False, default="root")
    page_token = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    page_size = serializers.IntegerField(required=False, min_value=1)
    trashed = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        page_token = attrs.get("page_token")
        if page_token == "":
            attrs["page_token"] = None
        return attrs


class BreadcrumbQuerySerializer(serializers.Serializer):
    item_id = serializers.CharField()


class DeleteItemQuerySerializer(serializers.Serializer):
    permanent = serializers.BooleanField(required=False, default=False)


class CreateFolderSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    parent_id = serializers.CharField(required=False, default="root")


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    name = serializers.CharField(required=False, max_length=255, allow_blank=False)
    parent_id = serializers.CharField(required=False, default="root")


class UpdateItemSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False, allow_blank=False)
    parent_id = serializers.CharField(required=False)

    def validate(self, attrs):
        if not attrs.get("name") and not attrs.get("parent_id"):
            raise serializers.ValidationError(
                "At least one of name or parent_id must be provided."
            )
        return attrs


class CopyItemSerializer(serializers.Serializer):
    parent_id = serializers.CharField()
    name = serializers.CharField(max_length=255, required=False)


class QuotaSummarySerializer(serializers.Serializer):
    quota_total_bytes = serializers.IntegerField(allow_null=True)
    quota_used_bytes = serializers.IntegerField(allow_null=True)
    quota_available_bytes = serializers.IntegerField(allow_null=True)


class BreadcrumbSerializer(serializers.Serializer):
    items = FileItemSerializer(many=True)
