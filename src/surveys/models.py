from django.db import models
from django.urls import reverse


class Survey(models.Model):
    text = models.TextField(default="")

    def get_absolute_url(self):
        return reverse("view_survey", args=[self.id])


class Question(models.Model):
    text = models.TextField(default="")
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, null=True, blank=True)
