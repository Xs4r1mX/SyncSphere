import secrets
from django.conf import settings


def generate_secure_token(length: int = None) -> str:
    """
    Generate a cryptographically secure URL-safe token.

    Args:
        length: Number of random bytes to use. Defaults to settings.SECURE_TOKEN_BYTES or 32.

    Returns:
        URL-safe random string.
    """
    if length is None:
        length = getattr(settings, "SECURE_TOKEN_BYTES", 32)

    return secrets.token_urlsafe(length)
