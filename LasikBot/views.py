from django.shortcuts import render
from django.views import generic
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .FacebookComm import FacebookComm
import json
from pprint import pprint


def session_test(request):
    if 'test_var' in request.session:
        print("Found test var: ", request.session['test_var'])
        print("Session key: ", request.session.session_key)
    else:
        print("Test var not found. Saving now")
        print("Session key: ", request.session.session_key)
        request.session['test_var'] = 'jason'
        print("Test var saved: ", request.session['test_var'])
        print("Session key: ", request.session.session_key)
    return HttpResponse()


# Create your views here.
class LasikBot(generic.View):
    facebook_comm = FacebookComm()
    user_id = None

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        print("Dispatching")
        return generic.View.dispatch(self, request, *args, **kwargs)

    # GET request handler
    def get(self, request):
        print("Received GET request")
        # todo error handling

        return self.facebook_comm.handle_get_request(request)

    def post(self, request):
        print("Received POST request")
        # Convert the text payload into a python dictionary
        incoming_message = json.loads(request.body.decode('utf-8'))

        self.facebook_comm.handle_post_request(incoming_message)

        return HttpResponse()
