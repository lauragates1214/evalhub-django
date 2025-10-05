from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = [os.environ.get("DJANGO_ALLOWED_HOST")]

# functional_tests stays in INSTALLED_APPS for staging
