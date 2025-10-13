from django.db import models
from django.conf import settings
from django.urls import reverse


class Survey(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="surveys",
    )
    name = models.CharField(max_length=200, default="")
    text = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse("instructors:survey_detail", args=[self.id])

    def get_qr_code_url(self):
        return f"/survey/{self.id}/"


class Question(models.Model):
    QUESTION_TYPES = [
        ("text", "Text"),
        ("multiple_choice", "Multiple Choice"),
        ("rating", "Rating Scale"),
        ("checkbox", "Checkboxes"),
        ("yes_no", "Yes/No"),
    ]

    text = models.TextField(default="")
    survey = models.ForeignKey(Survey, default=None, on_delete=models.CASCADE)
    question_type = models.CharField(
        max_length=20, choices=QUESTION_TYPES, default="text"
    )
    options = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ["id"]
        unique_together = ("survey", "text")


# Groups answers by user submission
class Submission(models.Model):
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name="submissions"
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(default="")
    comment_text = models.TextField(default="", blank=True)
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="answers"
    )
