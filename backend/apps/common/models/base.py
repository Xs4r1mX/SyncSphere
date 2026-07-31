import uuid

from django.db import models


class BaseModel(models.Model):
    """
    Base model inherited by all models in the application.

    Uses:
    - Integer primary key internally
    - UUID for public exposure
    - Common timestamps
    """

    id = models.BigAutoField(primary_key=True)

    uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
