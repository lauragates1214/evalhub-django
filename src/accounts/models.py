from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def get_by_natural_key(self, email):
        return self.get(email=email)


class User(AbstractBaseUser):
    email = models.EmailField(primary_key=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    is_active = True
    is_staff = False  # required by Django admin

    objects = UserManager()
