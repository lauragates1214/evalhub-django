from django.db import models
from django.urls import reverse


class Survey(models.Model):
    text = models.TextField(default="")

    def get_absolute_url(self):
        return reverse("view_survey", args=[self.id])


class Question(models.Model):
    text = models.TextField(default="")
    survey = models.ForeignKey(Survey, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return self.text  # to make admin list display meaningful

    class Meta:
        ordering = ["id"]
        unique_together = ("survey", "text")
