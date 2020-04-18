from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # URL to register with formstack webhook. Processes contact tracing form submission
    path('process_fs_webhook', views.process_fs_response_webhook),
    # URL to register with Twilio Webhook. Handles replies to our Twilio number
    path('receive_text', views.sms_reply),
    # "Positive test response" form and form processing
    path('test', views.test_form),
    # Redirect after "Positive test response" form is submitted
    path('thanks', views.thanks),
    # Dashboard that shows stats based on data in DB
    path('dashboard', views.dashboard),
    # Data in JSON form for dashboard
    path('dashboard_data', views.dashboard_data),
]

