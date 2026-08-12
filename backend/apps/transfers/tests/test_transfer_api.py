from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.cloud.services import ConnectionService
from apps.common.constants import ConnectionStatus, ProviderType
from apps.transfers.constants import TransferJobStatus, TransferOperation
from apps.transfers.models import TransferJob

User = get_user_model()


class TransferAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="xfer-api@example.com",
            first_name="T",
            last_name="Api",
            password="SecurePass123!",
        )
        self.other = User.objects.create_user(
            email="other-xfer@example.com",
            first_name="O",
            last_name="Ther",
            password="SecurePass123!",
        )
        self.source = ConnectionService.create_connection(
            user=self.user,
            provider=ProviderType.GOOGLE_DRIVE,
            display_name="Source",
            provider_account_id="src",
            credentials={"access_token": "a", "refresh_token": "r"},
            status=ConnectionStatus.ACTIVE,
        )
        self.dest = ConnectionService.create_connection(
            user=self.user,
            provider=ProviderType.GOOGLE_DRIVE,
            display_name="Dest",
            provider_account_id="dst",
            credentials={"access_token": "a2", "refresh_token": "r2"},
            status=ConnectionStatus.ACTIVE,
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    @patch("apps.transfers.tasks.run_transfer.execute_transfer.apply_async")
    def test_create_transfer(self, mock_apply_async):
        mock_apply_async.return_value = MagicMock(id="task-1")
        response = self.client.post(
            reverse("transfers:transfer-list-create"),
            {
                "operation": TransferOperation.COPY,
                "source_connection_uuid": str(self.source.uuid),
                "dest_connection_uuid": str(self.dest.uuid),
                "source_item_id": "file-1",
                "dest_parent_id": "root",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["operation"], TransferOperation.COPY)

    def test_get_other_user_job_404(self):
        job = TransferJob.objects.create(
            user=self.other,
            source_connection=ConnectionService.create_connection(
                user=self.other,
                provider=ProviderType.GOOGLE_DRIVE,
                display_name="O",
                provider_account_id="o1",
                credentials={"access_token": "a"},
                status=ConnectionStatus.ACTIVE,
            ),
            dest_connection=ConnectionService.create_connection(
                user=self.other,
                provider=ProviderType.GOOGLE_DRIVE,
                display_name="D",
                provider_account_id="o2",
                credentials={"access_token": "b"},
                status=ConnectionStatus.ACTIVE,
            ),
            operation=TransferOperation.COPY,
            source_item_id="x",
            status=TransferJobStatus.PENDING,
        )
        response = self.client.get(
            reverse("transfers:transfer-detail", kwargs={"job_uuid": job.uuid})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
