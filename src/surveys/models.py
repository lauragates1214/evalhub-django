from django.db import models
from django.conf import settings
from django.urls import reverse


class Survey(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE
    )
    text = models.TextField(default="")

    @property
    def name(self):
        return self.question_set.first().text

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
