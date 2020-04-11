from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('process_webhook', views.process_response_webhook, name='process_response_webhook'),
    # TODO remove this :)
    path('responses', views.survey_responses, name='responses'),
]

