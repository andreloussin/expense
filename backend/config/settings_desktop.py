from .settings import *

import os


# ============================
# Desktop mode
# ============================

APP_NAME = "ExpenseApp"
DEBUG = False

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

# ============================
# SQLite database
# ============================


if os.name == "nt":
    # Windows
    USER_DATA_DIR = Path(
        os.environ["APPDATA"]
    ) / APP_NAME

else:
    # Linux / Mac fallback
    USER_DATA_DIR = (
        Path.home()
        / f".{APP_NAME.lower()}"
    )


USER_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


DATABASE_PATH = USER_DATA_DIR / "database.sqlite3"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATABASE_PATH,
    }
}


# ============================
# Security
# ============================

SECRET_KEY = "desktop-secret-change-later"


# ============================
# Static
# ============================

STATIC_ROOT = BASE_DIR / "staticfiles"