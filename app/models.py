from django.db import models
from django.contrib.postgres.fields import JSONField


class SurveyInvitation(models.Model):
    """Represents a positive test result, resulting in an invitation to take the survey"""
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=256)
    phone_number = models.CharField(max_length=32)
    email = models.CharField(max_length=256)
    date_text_sent = models.DateTimeField(null=True)
    # TODO date_used is kinda redundant with SurveyResponse.invitation, refine data model.
    date_used = models.DateTimeField(null=True)


class SurveyResponse(models.Model):
    """Represents raw survey data coming from FormStack.
    Populated via FormStack webhook every time a survey is submitted"""
    created_at = models.DateTimeField(auto_now_add=True)
    raw_data = JSONField(blank=True, null=True)
    invitation = models.ForeignKey(SurveyInvitation, on_delete=models.DO_NOTHING, null=True)


class Contact(models.Model):
    """Represents a contact of a person who tested positive"""
    name = models.CharField(max_length=256)
    phone_number = models.CharField(max_length=32)
    email = models.CharField(max_length=256)
    # TODO remove nullable?
    reporter = models.ForeignKey(SurveyResponse, on_delete=models.DO_NOTHING, null=True)

