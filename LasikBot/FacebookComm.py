import json
import requests
from enum import Enum
from .ApplicationKey import ApplicationKey
from django.http import HttpResponse


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
            self.facebookId = data[ 'sender ' ][ 'id ' ]

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
    def handlePostRequest ( self, request, session ) :

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

                if (facebookData.requestType == MessageType.MESSAGE) :
                    self.processMessage ( facebookData, session )
                elif (facebookData.requestType == MessageType.POSTBACK) :
                    self.processPostback ( facebookData, session )
                    # todo handle delivery type messages?


    # ------------------------------------------------------------------------- #
    # Retrieves a Facebook user's first name
    # ------------------------------------------------------------------------- #
    # facebookId : the ID of the user whose first name is being requested
    # ------------------------------------------------------------------------- #
    # return  : user's first name
    # ------------------------------------------------------------------------- #
    def getUserFirstName ( self, facebookId ) :

        response = requests.get (
            'https://graph.facebook.com/v2.6/' + facebookId + '?access_token=' + ApplicationKey.applicationKey )
        responseData = response.json ( )

        if ('first_name' in responseData) :
            return responseData[ 'first_name' ]
        else :
            # todo error handling
            return None


    # ------------------------------------------------------------------------- #
    # STATIC METHODS
    # ------------------------------------------------------------------------- #
    def processMessage ( self, facebookData, session ) :

        if ('facebookId' in session) :
            # continue the conversation
            nextMessage = "What's the best email address for you?"
            self.sendMessage ( facebookData.facebookId, nextMessage )

        else :
            # create session and say hi
            session[ 'facebookId' ] = facebookData.facebookId
            # todo set expiration data

            self.sendGreeting( facebookData.facebookId )
            self.sendConfirmationButtons( facebookData.facebookId )


    def sendGreeting ( self, facebookId ):

        # todo fetch the <PRACTICE NAME> based on the page id
        welcomeMessage = ("Hello, " + self.getUserFirstName ( facebookId ) + "! Thanks for "
            "choosing <PRACTICE NAME>. I'm here to help you schedule your free LASIK consultation. "
            "I just need a couple more pieces of information.")

        self.sendMessage ( facebookId, welcomeMessage )


    def sendConfirmationButtons ( self, facebookId ):
        post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + ApplicationKey.applicationKey
        response_msg = json.dumps ( { "recipient": { "id": facebookId }, "message": {
            "attachment": { "type": "template",
                            "payload": { "template_type": "button", "text": "Let's get started!", "buttons": [
                                { "type": "postback", "title": "Ok", "payload": "ok" },
                                { "type": "postback", "title": "Maybe later", "payload": "later" } ] } } } } )

        status = requests.post ( post_message_url, headers = { "Content-Type": "application/json" }, data = response_msg )
        # todo error handling


    def processPostback ( self, facebookData, session ) :

        botMessage = None
        if ( facebookData.payload == "ok" ):
            botMessage = "What's the best email address for you?"

        elif ( facebookData.payload == "later" ):
            botMessage = "Sounds good! Just stop back by when you want to schedule your free consultation"

        self.sendMessage ( facebookData.facebookId, botMessage )

