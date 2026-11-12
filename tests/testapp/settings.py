import os

from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DATABASE_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DATABASE_NAME", "django_bucketav.sqlite3"),
        "USER": os.environ.get("DATABASE_USER", None),
        "PASSWORD": os.environ.get("DATABASE_PASS", None),
        "HOST": os.environ.get("DATABASE_HOST", None),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "default-location",
    },
}

INSTALLED_APPS = [
    "django_bucketav",
    "django_bucketav.wagtail",
    "testapp",
    "wagtail.users",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.admin",
    "wagtail.sites",
    "wagtail",
    "taggit",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

if DATABASES["default"]["ENGINE"] != "django.db.backends.sqlite3":
    INSTALLED_APPS += ["django.contrib.postgres"]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "testapp.urls"
SECRET_KEY = "not-a-secret"  # noqa: S105

TIME_ZONE = "Europe/London"
USE_TZ = True

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

DEFAULT_FILE_STORAGE = "inmemorystorage.InMemoryStorage"


STATICFILES_DIRS = [PROJECT_DIR / "static"]

STATIC_ROOT = PROJECT_DIR / "test-static"
STATIC_URL = "/static/"

MEDIA_ROOT = PROJECT_DIR / "test-media"

# Wagtail settings
WAGTAIL_SITE_NAME = "Wagtail Sharepoint test site"
WAGTAILADMIN_BASE_URL = "http://testserver"
WAGTAILDOCS_DOCUMENT_MODEL = "testapp.CustomDocument"

SNS_VERIFY_CERTIFICATE = False


# our package config
DJANGO_BUCKETAV = {
    "MODELS": {
        "testapp.MyModelWithBucketAVMixin": ["file"],
    }
}
