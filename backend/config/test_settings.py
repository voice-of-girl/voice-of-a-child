"""
Django settings used only by the automated test-suite.

Everything is inherited from the base settings; the overrides below make
tests deterministic and hermetic: throttling is disabled (many requests
come from one address), password hashing is fast, the cache is local and
generated report files land in a throw-away directory instead of the
developer's media folder.
"""
import tempfile

from config.settings import *  # noqa: F401,F403

REST_FRAMEWORK = dict(REST_FRAMEWORK)  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = ()
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "voice-test-cache",
    }
}

# Only used to authenticate during tests; not a security boundary here.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

MEDIA_ROOT = tempfile.mkdtemp(prefix="voice-test-media-")
