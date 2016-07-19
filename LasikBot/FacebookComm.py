import json
import requests
from enum import Enum
from . import ApplicationKey
from django.http import HttpResponse
from pprint import pprint
from .models import Client, FacebookUser, Lead, Availability


class MessageType ( Enum ) :
    MESSAGE  = 0
    POSTBACK = 1
    DELIVERY = 2


class FacebookData ( ) :
    pageId      = None
    updateTime  = None
    facebookId  = None
    text        = None
    payload     = None
    requestType = None

    def __init__ ( self, data, pageId, updateTime ) :

        self.pageId = pageId
        self.updateTime = updateTime

        if ('sender' in data) :
            self.facebookId = data[ 'sender' ][ 'id' ]

        if ('message' in data) :
            self.requestType = MessageType.MESSAGE
            self.text = data[ 'message' ][ 'text' ]

        elif ('postback' in data) :
            self.requestType = MessageType.POSTBACK
            self.payload = data[ 'postback' ][ 'payload' ]


# This class serves as the interface to the Facebook Messenger API
class FacebookComm ( ) :

    # ------------------------------------------------------------------------- #
    # Sends a POST message to Facebook Messenger
    # ------------------------------------------------------------------------- #
    # facebookId : the ID of the user to which we're sending the message
    # message    : the message to send
    # ------------------------------------------------------------------------- #
    # return     : n/a
    # ------------------------------------------------------------------------- #
    def sendMessage ( self, facebookID, message ) :

        # todo Eventually I'll need to fetch the pageKey from the database as each will be unique to a customer
        pageKey = ApplicationKey.applicationKey  # todo error handling if this is doesn't get set
        postUrl = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + pageKey
        response_msg = json.dumps ( { "recipient" : { "id" : facebookID }, "message" : { "text" : message } } )

        # todo: error handling
        requests.post ( postUrl, headers = { "Content-Type" : "application/json" }, data = response_msg )

    # ------------------------------------------------------------------------- #
    # Handles a Facebook GET request
    # ------------------------------------------------------------------------- #
    # request : the GET request that was received
    # ------------------------------------------------------------------------- #
    # return  : HttpResponse
    # ------------------------------------------------------------------------- #
    def handleGetRequest ( self, request ) :
        print ( "Handling GET request" )
        if request.GET[ 'hub.verify_token' ] == ApplicationKey.getApplicationToken ( ) :
            return HttpResponse ( request.GET[ 'hub.challenge' ] )
        else :
            # todo error handling
            print ( "Error in authentication" )
            return HttpResponse ( "Error in authentication" )

    # ------------------------------------------------------------------------- #
    # Handles a Facebook POST request
    # ------------------------------------------------------------------------- #
    # request : the POST request that was received
    # ------------------------------------------------------------------------- #
    # return  : HttpResponse
    # ------------------------------------------------------------------------- #
    def handlePostRequest ( self, request ):
        print ("FacebookComm.handlePostRequest")

        # the format for incoming Facebook messages is the following:
        #   "object" : "page"
        #   "entry"  : [ array of entry objects ]
        #       "entry" : { "page id", "time of update", [ array of messaging objects ] }
        #           "messaging" : { "sender id", "recipient id", ... (callback specific fields) }

        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in request[ 'entry' ] :
            pageId = entry[ 'id' ]
            updateTime = entry[ 'time' ]

            for message in entry[ 'messaging' ] :
                print ( message )
                facebookData = FacebookData ( message, pageId, updateTime )

                if (facebookData.requestType == MessageType.MESSAGE ):
                    print ( "Processing message" )
                    self.processMessage ( facebookData )

                elif (facebookData.requestType == MessageType.POSTBACK ):
                    print ( "Processing postback" )
                    self.processPostback ( facebookData )
                    # todo handle delivery type messages?


    # ------------------------------------------------------------------------- #
    # Retrieves a Facebook user's first name
    # ------------------------------------------------------------------------- #
    # facebookId : the ID of the user whose first name is being requested
    # ------------------------------------------------------------------------- #
    # return  : user's first name
    # ------------------------------------------------------------------------- #
    def getUserFirstName ( self, facebookId ) :
        print ( "fetching first name" )
        response = requests.get ('https://graph.facebook.com/v2.6/' +
                                 str(facebookId) + '?access_token=' +
                                 ApplicationKey.applicationKey )

        responseData = response.json ( )

        pprint ( responseData )

        if ('first_name' in responseData) :
            return responseData[ 'first_name' ]
        else :
            # todo error handling
            return None


    # ------------------------------------------------------------------------- #
    # STATIC METHODS
    # ------------------------------------------------------------------------- #
    def processMessage ( self, facebookData ) :

        user = None

        try:
            user = FacebookUser.objects.get ( facebookId = facebookData.facebookId )
        except FacebookUser.DoesNotExist:
           user = None

        # IF USER IN DATABASE
        if ( user is not None ):
            print ( "I have talked to this user before" )

            # IF EMAIL IS IN DATABASE
            if ( user.emailAddress is None ):
                print ( "I still need to get an email" )
                facebookData.payload = "OK"
                processPostback ( facebookData )
                # IF THEY HAVE AN APPOINTMENT BOOKED
                    # IF THE CONSULTATION IS IN THE PAST
                        # IGNORE ??
                    # ELSE
                        # ASK IF THEY WOULD LIKE TO RESCHEDULE
                # ELSE
                    # ASK IF THEY WOULD LIKE TO SCHEDULE A CONSULTATION
            # ELSE
                # IF THEY PROVIDED A VALID EMAIL ADDRESS 
                    # SAVE THE EMAIL
                # ELSE
                    # ASK FOR THE EMAIL AGAIN
                    
                
            
        else:
            # SEND GREETING
            print ( "Saving new user and sending greeting" )
            user = FacebookUser ( facebookId = facebookData.facebookId )
            user.save()
            self.sendGreeting( facebookData )


    def sendGreeting ( self, facebookData ):
        firstName = self.getUserFirstName ( facebookData.facebookId )
        practiceName = None
        intro = "Hey there!"

        try:
            practiceName = Client.objects.get ( facebookPageId = facebookData.pageId )
        except Client.DoesNotExist:
            practiceName = "<PRACTICE NAME>"

        if ( firstName is not None ):
            intro = "Hi, " + firstName + "!"

        # todo fetch the <PRACTICE NAME> based on the page id
        welcomeMessage = ( intro + " Thanks for "
            "choosing " + practiceName + ". I'm here to help you schedule your free LASIK consultation. "
            "I just need a couple more pieces of information. Let's get started!")

        buttonPayload = [ { "type": "postback", "title": "OK", "payload": "OK" } ]

        self.sendButtons ( facebookData.facebookId, welcomeMessage, buttonPayload )



    def sendButtons ( self, facebookId, message, payload ):

        print ( "Sending callback buttons" )
        postMessageUrl = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + ApplicationKey.applicationKey
        callbackMessage = json.dumps ( { "recipient": { "id": facebookId }, "message": {
            "attachment": { "type": "template",
                            "payload": { "template_type": "button", "text": message, "buttons": payload }
                            } } } )

        status = requests.post ( postMessageUrl, headers = { "Content-Type": "application/json" },
                                 data = callbackMessage )
        # todo error handling


    def processPostback ( self, facebookData ) :

        botMessage = None
        if ( facebookData.payload == "OK" ):
            print ( "Received 'ok' postback" )
            botMessage = "What's the best email address for you?"

        elif ( facebookData.payload == "later" ):
            print ( "Recieved 'later' postback" )
            botMessage = "Sounds good! Just stop back by when you want to schedule your free consultation"

        self.sendMessage ( facebookData.facebookId, botMessage )

