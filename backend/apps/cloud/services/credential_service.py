import json
import logging
from typing import Any

from apps.common.exceptions import CredentialEncryptionException
from apps.common.utils import CredentialCipher

logger = logging.getLogger(__name__)


class CredentialService:
    """Encrypts and decrypts provider credential payloads for storage."""

    @staticmethod
    def encrypt_payload(payload: dict[str, Any]) -> str:
        if not isinstance(payload, dict):
            raise CredentialEncryptionException("Credentials payload must be a dict.")

        try:
            plaintext = json.dumps(payload, separators=(",", ":"), sort_keys=True)
        except (TypeError, ValueError) as exc:
            raise CredentialEncryptionException(
                "Credentials payload is not JSON-serializable."
            ) from exc

        return CredentialCipher.encrypt(plaintext)

    @staticmethod
    def decrypt_payload(ciphertext: str) -> dict[str, Any]:
        plaintext = CredentialCipher.decrypt(ciphertext)

        try:
            payload = json.loads(plaintext)
        except json.JSONDecodeError as exc:
            logger.error("Decrypted credentials were not valid JSON.")
            raise CredentialEncryptionException(
                "Stored credentials are corrupted."
            ) from exc

        if not isinstance(payload, dict):
            raise CredentialEncryptionException("Stored credentials are corrupted.")

        return payload

    @staticmethod
    def wipe() -> str:
        """Return an empty ciphertext placeholder after unlink."""
        return ""
