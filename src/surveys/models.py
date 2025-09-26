from django.db import models


class Survey(models.Model):
    text = models.TextField(default="")


class Question(models.Model):
    text = models.TextField(default="")
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, null=True, blank=True)
