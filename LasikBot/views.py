from django.shortcuts import render
from django.views import generic
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import appkey


# Create your views here.
class LasikBot ( generic.View ):

    @method_decorator ( csrf_exempt )
    def dispatch ( self, request, *args, **kwargs ):
        return generic.View.dispatch ( self, request, *args, **kwargs )

    # GET request handler
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == appkey.releaseToken:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            print "Error in authentication"
            return HttpResponse("Error in authentication")


    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                print "MESSAGE RECEIVED:"
                print message
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events
                if 'message' in message:
                    user_id = message['sender']['id']
                    # Print the message to the terminal
                    if (messageIsGreeting(message)):
                        response = requests.get(
                            'https://graph.facebook.com/v2.6/' + user_id + '?access_token=' + appkey.appkey)
                        post_facebook_message(user_id, "Hi there, " + response.json()['first_name'])
                    elif (messageIsButtons(message)):
                        post_facebook_buttons(user_id)
                    else:
                        post_facebook_message(user_id, message['message']['text'])
                elif 'postback' in message:
                    user_id = message['sender']['id']
                    handlePostback(user_id, message['postback']['payload'])

        return HttpResponse()
