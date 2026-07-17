import os
from .base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()]

CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]

# nginx terminates the connection in front of Django on the same box (per
# Tayo's deployment plan) and forwards this header, so trust it for HTTPS
# detection.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = os.environ.get("DJANGO_HTTPS", "1") == "1"
CSRF_COOKIE_SECURE = os.environ.get("DJANGO_HTTPS", "1") == "1"
SECURE_SSL_REDIRECT = os.environ.get("DJANGO_HTTPS", "1") == "1"
