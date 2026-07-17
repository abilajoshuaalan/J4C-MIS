from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["*"]

# SQLite fallback for local dev so you don't need Postgres running just to
# poke around the admin. Prod always uses Postgres (see base.py + prod.py).
if os.environ.get("USE_SQLITE", "1") == "1":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
