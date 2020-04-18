import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app.models import SurveyResponse, Contact, SurveyInvitation
from surveybackend.settings import TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from random import randint
from datetime import datetime
from app.forms import PositiveTestForm
from django.forms.models import model_to_dict

CONTRACT_TRACING_FORM_URL = "https://survey.nexttrace.now.sh/formstack/"

POS_RESULT_TEXT= """This is just a test! MESSAGE FROM PUBLIC HEALTH NEW YORK:
Hi {}. We are sorry to inform you that you have tested positive for COVID-19. We ask that you please self-isolate for the next 7 days or until 3 days after your symptoms begin to improve, whichever is longer. If your symptoms get worse, please phone your primary care practitioner to seek guidance before going to the hospital. If you do not have a primary care practitioner, please contact XXXX.

In an effort to stop transmission of COVID-19, the public health department is asking individuals who have COVID-19 to answer a 15 minute survey to find people you may have had contact with while you were infectious. Your participation will help us find other people who might have COVID-19 before they transmit their infection to someone else. You can find the survey at: {}. Please enter unique code {} in the survey to identify yourself."
"""

CONTACT_TEXT = """Hi {}! This is just a test! Please be advised that you have had contact with an individual to tested positive for COVID-19. Given that you could be infected, and could transmit COVID-19 to other people even if you do not feel symptoms, we ask that you self-quarantine for the next 14 days. To schedule testing, please go here <URL to testing ideally>. We also recommend monitoring your symptoms with our symptom tracker <go here>."""


def index(request):
    return HttpResponse("Hello, world. You're at the index.")


def test_form(request):
    """View for displaying + processing the "positive test result" form"""

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PositiveTestForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print(form.cleaned_data)
            name = form.cleaned_data.get('name')
            phone = form.cleaned_data.get('phone')

            # Create a survey invitation for the person who tested positive
            code = randint(1000000, 10000000)
            invite = SurveyInvitation(code=code, name=name, phone_number=phone)
            invite.save()

            # Send a text message to the person
            send_pos_result_text(name, phone, code)
            invite.date_text_sent = datetime.now()
            invite.save()

            return HttpResponseRedirect(f"/app/thanks?name={name}&phone={phone}")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = PositiveTestForm()

    return render(request, 'test.html', {'form': form})

def thanks(request):
    """Message displayed after filling out the the "positive test result" form"""
    name = request.GET.get("name")
    phone = request.GET.get("phone")
    return HttpResponse(f"Thanks for filling out the form. We've messaged {name} at {phone}.")


@csrf_exempt
def process_fs_response_webhook(request):
    """Process a contract tracing form from FormStack.
    This is called by a webhook after the form is filled out"""
    if not request.body:
        return HttpResponse("This is the response webhook")

    # TODO authenticate that http call is coming from formstack
    body = json.loads(request.body)
    print(body)

    survey_resp = SurveyResponse(raw_data=body)
    survey_resp.save()

    # Find matching survey invitation
    code = body['unique_code']
    try:
        invitation = SurveyInvitation.objects.get(code=code)
        survey_resp.invitation = invitation
        survey_resp.save()
        invitation.date_used = datetime.now()
        invitation.save()
    except SurveyInvitation.DoesNotExist:
        print("No matching invitation found")

    # For each contact reported, save the contact to the DB and text the contact
    # TODO make a more general way of finding all contacts
    for i in range(1, 10):
        name_key = f"name_{i}"
        phone_key = f"phone_{i}"
        if not body.get(name_key):
            continue
        name_json = body[name_key]
        contact_name = f"{name_json['first']} {name_json['last']}"
        contact_phone = body[phone_key]
        new_contact = Contact(name=contact_name, phone_number=contact_phone,
                              reporter=survey_resp)
        new_contact.save()

        if contact_phone:
            send_contact_text(contact_name, contact_phone)

    return JsonResponse(body)


def send_text(phone, text_message):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
                 body=text_message,
                 from_=TWILIO_FROM_NUMBER,
                 to=phone
            )

    print(message.sid)
    # TODO use callback to check if message was delivered successfully


def send_pos_result_text(name, phone, code):
    text_message = POS_RESULT_TEXT.format(name, CONTRACT_TRACING_FORM_URL, code)
    send_text(phone, text_message)


def send_contact_text(name, phone):
    text_message = CONTACT_TEXT.format(name)
    send_text(phone, text_message)


@csrf_exempt
def sms_reply(request):
    """Handle an SMS sent to our Twilio phone number"""
    print(f"Received SMS reply. Body: {request.body}")

    text_content = request.POST.get('Body')
    from_number = request.POST.get('From')
    print(text_content, from_number)

    # Create + send response
    resp = MessagingResponse()
    msg = f"Thanks for replying! <TODO content here>."
    resp.message(msg)
    return HttpResponse(str(resp))


def get_stats():
    num_positive_results = SurveyInvitation.objects.count()
    num_reported_contacts = Contact.objects.count()
    num_completed_forms = SurveyResponse.objects.count()
    list_unused_codes = SurveyInvitation.objects.filter(date_used=None)
    return {
        "num_positive_results": num_positive_results,
        "num_reported_contacts": num_reported_contacts,
        "num_completed_forms": num_completed_forms,
        "list_unused_codes": list_unused_codes,
    }


def dashboard(request):
    return render(request, 'dashboard.html', get_stats())


def dashboard_data(request):
    data = get_stats()
    data["list_unused_codes"] = [model_to_dict(obj) for obj in data["list_unused_codes"]]
    return JsonResponse(data)
