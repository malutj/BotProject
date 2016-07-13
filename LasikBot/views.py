from django.shortcuts import render
from django.views import generic
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from . import appkey
from . import FacebookComm
import json


# Create your views here.
class LasikBot ( generic.View ):

    fbComm = FacebookComm

    @method_decorator ( csrf_exempt )
    def dispatch ( self, request, *args, **kwargs ):
        return generic.View.dispatch ( self, request, *args, **kwargs )

    # GET request handler
    def get ( self, request, *args, **kwargs ):
        if self.request.GET[ 'hub.verify_token' ] == appkey.releaseToken:
            return HttpResponse ( self.request.GET[ 'hub.challenge' ] )
        else:
            print ( "Error in authentication" )
            return HttpResponse ( "Error in authentication" )


    def post ( self, request, *args, **kwargs ):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads ( self.request.body.decode ( 'utf-8' ) )

        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message[ 'entry' ]:
            for message in entry[ 'messaging' ]:
                print ( message )

        return HttpResponse ( )
