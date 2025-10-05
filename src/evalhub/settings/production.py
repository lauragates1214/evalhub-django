from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = [os.environ.get("DJANGO_ALLOWED_HOST")]

# Remove functional_tests from INSTALLED_APPS
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "functional_tests"]
