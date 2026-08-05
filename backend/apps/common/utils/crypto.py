import logging

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

from apps.common.exceptions.cloud import CredentialEncryptionException

logger = logging.getLogger(__name__)


class CredentialCipher:
    """
    Symmetric encryption helper for cloud provider credentials.

    Uses Fernet with CREDENTIALS_ENCRYPTION_KEY from settings.
    """

    @staticmethod
    def _get_fernet() -> Fernet:
        key = getattr(settings, "CREDENTIALS_ENCRYPTION_KEY", None)
        if not key:
            raise CredentialEncryptionException(
                "CREDENTIALS_ENCRYPTION_KEY is not configured."
            )

        try:
            key_bytes = key.encode("utf-8") if isinstance(key, str) else key
            return Fernet(key_bytes)
        except Exception as exc:
            logger.error("Invalid CREDENTIALS_ENCRYPTION_KEY configuration.")
            raise CredentialEncryptionException(
                "Invalid credential encryption key configuration."
            ) from exc

    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        if plaintext is None:
            raise CredentialEncryptionException("Cannot encrypt empty credentials.")

        try:
            token = cls._get_fernet().encrypt(plaintext.encode("utf-8"))
            return token.decode("utf-8")
        except CredentialEncryptionException:
            raise
        except Exception as exc:
            logger.error("Credential encryption failed.")
            raise CredentialEncryptionException() from exc

    @classmethod
    def decrypt(cls, ciphertext: str) -> str:
        if not ciphertext:
            raise CredentialEncryptionException("Cannot decrypt empty credentials.")

        try:
            plaintext = cls._get_fernet().decrypt(ciphertext.encode("utf-8"))
            return plaintext.decode("utf-8")
        except InvalidToken as exc:
            logger.error("Credential decryption failed: invalid token.")
            raise CredentialEncryptionException(
                "Stored credentials could not be decrypted."
            ) from exc
        except CredentialEncryptionException:
            raise
        except Exception as exc:
            logger.error("Credential decryption failed.")
            raise CredentialEncryptionException() from exc

    @staticmethod
    def generate_key() -> str:
        """Generate a new Fernet key suitable for CREDENTIALS_ENCRYPTION_KEY."""
        return Fernet.generate_key().decode("utf-8")
