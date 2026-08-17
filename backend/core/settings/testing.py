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

DROPBOX_OAUTH_APP_KEY = "test-dropbox-app-key"
DROPBOX_OAUTH_APP_SECRET = "test-dropbox-app-secret"
DROPBOX_OAUTH_REDIRECT_URI = "http://testserver/api/cloud/providers/dropbox/callback/"

ONEDRIVE_OAUTH_CLIENT_ID = "test-onedrive-client-id"
ONEDRIVE_OAUTH_CLIENT_SECRET = "test-onedrive-client-secret"
ONEDRIVE_OAUTH_REDIRECT_URI = "http://testserver/api/cloud/providers/onedrive/callback/"
ONEDRIVE_OAUTH_TENANT = "common"

MAX_FILE_UPLOAD_SIZE_BYTES = 104857600
FILE_LIST_DEFAULT_PAGE_SIZE = 50
FILE_LIST_MAX_PAGE_SIZE = 100

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

MAX_TRANSFER_SIZE_BYTES = 104857600

