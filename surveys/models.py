from django.db import models


class Survey(models.Model):
    text = models.TextField(default="")


class Question(models.Model):
    text = models.TextField(default="")
