"""
Django settings for the Voice of a Girl impact measurement platform.

Configuration is driven entirely through environment variables so that no
secrets are committed to the repository. See backend/.env.example for the
full list of supported variables.
"""
import os
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Core Django settings
# --------------------------------------------------------------------------
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-CHANGE-ME-voice-of-a-girl-982341",  # noqa: S105
)
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    # First-party apps
    "apps.core",
    "apps.accounts",
    "apps.organisations",
    "apps.participants",
    "apps.programmes",
    "apps.surveys",
    "apps.monitoring",
    "apps.analytics",
    "apps.reports",
    "apps.impact_projects",
    "apps.ussd",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------
# Default: SQLite (zero-config local development). In production set
# DATABASE_URL to a PostgreSQL connection string.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
if os.getenv("DATABASE_URL"):
    import dj_database_url  # type: ignore

    DATABASES["default"] = dj_database_url.config(conn_max_age=600)

# --------------------------------------------------------------------------
# Authentication
# --------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.CustomUser"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=int(os.getenv("ACCESS_TOKEN_HOURS", "6"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("REFRESH_TOKEN_DAYS", "7"))),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
}

# --------------------------------------------------------------------------
# Internationalisation / static / media
# --------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise serves collected static files in production (Render).
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# --------------------------------------------------------------------------
# Django REST Framework
# --------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": ("rest_framework.throttling.ScopedRateThrottle",),
    "DEFAULT_THROTTLE_RATES": {
        "login": os.getenv("THROTTLE_LOGIN", "10/min"),
        "public_survey": os.getenv("THROTTLE_PUBLIC_SURVEY", "120/hour"),
        "public_submit": os.getenv("THROTTLE_PUBLIC_SUBMIT", "10/hour"),
        "default": os.getenv("THROTTLE_DEFAULT", "120/min"),
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Voice of a Girl Impact Platform API",
    "DESCRIPTION": (
        "Secure multi-tenant impact measurement and programme management "
        "platform. Public survey endpoints require no authentication; all "
        "other endpoints require a JWT and are scoped to the caller's "
        "organisation."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

# --------------------------------------------------------------------------
# CORS (cross-origin requests from the React frontend)
# --------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True

# --------------------------------------------------------------------------
# Security hardening
# --------------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() in ("1", "true")
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Public survey link base URL (used when building shareable survey URLs)
PUBLIC_SURVEY_BASE_URL = os.getenv("PUBLIC_SURVEY_BASE_URL", "http://localhost:5173")
# Report storage location (overridable for object storage abstractions later).
REPORT_STORAGE_ROOT = BASE_DIR / "media" / "reports"

# USSD / Africa's Talking
AFRICASTALKING_USERNAME = os.getenv("AFRICASTALKING_USERNAME", "")
AFRICASTALKING_API_KEY = os.getenv("AFRICASTALKING_API_KEY", "")
AFRICASTALKING_USSD_SERVICE_CODE = os.getenv("AFRICASTALKING_USSD_SERVICE_CODE", "")
AFRICASTALKING_USSD_CALLBACK_URL = os.getenv("AFRICASTALKING_USSD_CALLBACK_URL", "")
USSD_MAX_CALLS_PER_MINUTE = int(os.getenv("USSD_MAX_CALLS_PER_MINUTE", "30"))
