from django.shortcuts import render
from django.views import generic
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .FacebookComm import FacebookComm
import json


# Create your views here.
class LasikBot ( generic.View ):

    facebookComm = FacebookComm ( )
    userId = None


    @method_decorator ( csrf_exempt )
    def dispatch ( self, request, *args, **kwargs ):
        return generic.View.dispatch ( self, request, *args, **kwargs )


    # GET request handler
    def get (self, request):

        # todo error handling
        return self.facebookComm.handleGetRequest ( request )


    def post ( self, request ):

        # Converts the text payload into a python dictionary
        incomingMessage = json.loads ( request.body.decode ( 'utf-8' ) )

        self.facebookComm.handlePostRequest ( incomingMessage, request.session )

        return HttpResponse ( )
