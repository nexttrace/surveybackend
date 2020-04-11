import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app.models import SurveyResponse
from surveybackend.settings import SURVEY_MONKEY_TOKEN
import requests

# TODO remove
SURVEY_ID = 281690550

def index(request):
    return HttpResponse("Hello, world. You're at the index.")


def requests_session():
    s = requests.session()
    s.headers.update({
        "Authorization": "Bearer %s" % SURVEY_MONKEY_TOKEN,
        "Content-Type": "application/json"
    })
    return s


def survey_responses(request):
    s = requests_session()
    url = f"https://api.surveymonkey.com/v3/surveys/{SURVEY_ID}/responses/bulk"
    payload = {"per_page": 40}
    resp = s.get(url, params=payload).json()
    print(resp)

    return JsonResponse(resp)


@csrf_exempt
def process_response_webhook(request):
    # TODO authenticate that http call is coming from surveymonkey
    if not request.body:
        return HttpResponse("Welcome to response webhook")

    body = json.loads(request.body)
    print(body)
    response_id = body["object_id"]
    survey_id = body["resources"]["survey_id"]

    s = requests_session()
    url = f"https://api.surveymonkey.net/v3/surveys/{survey_id}/responses/{response_id}/details"
    resp = s.get(url).json()

    print(resp)

    # TODO get survey answers
    # TODO get from DB instead!
    survey_url = f"https://api.surveymonkey.net/v3/surveys/{survey_id}/details"

    # TODO join response with answers

    # TODO parse out structured fields

    # TODO save into db w/ structured fields, raw response, answer response?
    db_obj = SurveyResponse(raw_data=resp)
    db_obj.save()

    return JsonResponse(resp)


@csrf_exempt
def process_survey_change_webhook(request):
    # TODO authenticate that http call is coming from surveymonkey
    if not request.body:
        return HttpResponse("Welcome to survey change/create webhook")

    body = json.loads(request.body)
    print(body)

    # TODO:
    # get actual survey
    # Save as version w/ survey json

    return JsonResponse(body)