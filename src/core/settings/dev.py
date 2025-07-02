import os

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-_odb62l=_u11+bj4a#@7g(hwhsik3e3_c5lti^g%1(h3)!!r1_",
)

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


try:
    from .local import *
except ImportError:
    pass
