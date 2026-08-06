from cryptography.fernet import Fernet

from .base import *  # noqa: F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

CREDENTIALS_ENCRYPTION_KEY = Fernet.generate_key().decode()

GOOGLE_OAUTH_CLIENT_ID = "test-google-client-id"
GOOGLE_OAUTH_CLIENT_SECRET = "test-google-client-secret"
GOOGLE_OAUTH_REDIRECT_URI = "http://testserver/api/cloud/providers/google_drive/callback/"
