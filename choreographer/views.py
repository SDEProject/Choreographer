import requests
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

# Create your views here.
from django.views import View
from requests import Response
from rest_framework import viewsets, mixins
from travelando import settings
import json


# Create your views here.
class OrchestratorView(View):
    def get(self, request):
        parameters = request.GET
        response = requests.get(f"http://{settings.SERVICE_BUSINESS_LOGIC_HOST}:{settings.SERVICE_BUSINESS_LOGIC_PORT}/{settings.SERVICE_BUSINESS_LOGIC}/search", parameters)
        return JsonResponse(response.json(), safe=False)

    def post(self, request):
        body = request.body.decode('utf-8')
        json_request = json.loads(body)
        print(json_request)
        # print(json_request['queryResult']['parameters'])
        parameters = json_request['queryResult']['parameters']
        parameters['intentName'] = json_request['queryResult']['intent']['displayName']
        response = {
                    "fulfillmentMessages": [
                        {
                          "text": {
                            "text": ["Sorry, I'm not able to manage your request."]
                          }
                        }
                      ]
                    }

        print(parameters)
        if parameters['intentName'] == 'search':
            print('choreogr search')
            response = requests.get(f"http://{settings.SERVICE_PROCESS_CENTRIC_HOST}:{settings.SERVICE_PROCESS_CENTRIC_PORT}/{settings.SERVICE_PROCESS_CENTRIC}/searches", parameters)
        elif parameters['intentName'] == 'save':
            context = json_request['queryResult']['outputContexts'][0]['parameters']
            save_parameters = {
                "context": context,
                "request_parameters": parameters
            }
            response = requests.post(f"http://{settings.SERVICE_PROCESS_CENTRIC_DB_HOST}:{settings.SERVICE_PROCESS_CENTRIC_DB_PORT}/{settings.SERVICE_PROCESS_CENTRIC_DB}/save/", None, save_parameters)
        elif parameters['intentName'] == 'retrieve':
            response = requests.get(
                f"http://{settings.SERVICE_PROCESS_CENTRIC_DB_HOST}:{settings.SERVICE_PROCESS_CENTRIC_DB_PORT}/{settings.SERVICE_PROCESS_CENTRIC_DB}/retrieve/", parameters)
        elif parameters['intentName'] == 'delete':
            response = requests.post(f"http://{settings.SERVICE_PROCESS_CENTRIC_DB_HOST}:{settings.SERVICE_PROCESS_CENTRIC_DB_PORT}/{settings.SERVICE_PROCESS_CENTRIC_DB}/delete/", None, parameters)
        else:
            print('Sorry, I cannot manage your request.')
        return JsonResponse(response.json(), safe=False)
