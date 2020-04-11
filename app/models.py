from django.db import models
from django.contrib.postgres.fields import JSONField


class SurveyResponse(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    raw_data = JSONField(blank=True, null=True)
