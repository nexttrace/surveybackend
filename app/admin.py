from django.contrib import admin
from app.models import SurveyResponse, SurveyInvitation, Contact

admin.site.register(SurveyInvitation)
admin.site.register(SurveyResponse)
admin.site.register(Contact)