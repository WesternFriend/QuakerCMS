import os

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-development-key-change-in-production",
)

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Development-only apps for Tailwind CSS live reload
if DEBUG:
    INSTALLED_APPS += ["django_browser_reload"]

# Development-only middleware for browser reload
if DEBUG:
    MIDDLEWARE += ["django_browser_reload.middleware.BrowserReloadMiddleware"]


try:
    from .local import *
except ImportError:
    pass
