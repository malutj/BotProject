import json
import requests
from enum import Enum
from ApplicationKey import ApplicationKey
from django.http import HttpResponse


class MessageType ( Enum ):
    MESSAGE  = 0
    POSTBACK = 1
    DELIVERY = 2


class FacebookData ( ):
    facebookId  = None
    text        = None
    payload     = None
    requestType = None

    def __init__ ( self, data ):

        if ( 'sender' in data ):
            self.facebookId = data[ 'sender '][ 'id ']

        if ( 'message' in data ):
            self.requestType = MessageType.MESSAGE
            self.text = data[ 'message' ][ 'text' ]
        elif ( 'postback' in data ):
            self.requestType = MessageType.POSTBACK
            self.payload = data[ 'postback' ][ 'payload' ]


# This class serves as the interface to the Facebook Messenger API
class FacebookComm ( ):

    # ------------------------------------------------------------------------- #
    # Sends a POST message to Facebook Messenger
    # ------------------------------------------------------------------------- #
    # facebookId : the ID of the user to which we're sending the message
    # message    : the message to send
    # ------------------------------------------------------------------------- #
    # return     : n/a
    # ------------------------------------------------------------------------- #
    def sendMessage ( self, facebookID, message ):

        pageKey = ApplicationKey.applicationKey # todo error handling if this is doesn't get set
        postUrl = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + pageKey
        response_msg = json.dumps ( { "recipient": { "id": facebookID }, "message": { "text": message } } )

        # todo: error handling
        requests.post(postUrl, headers={"Content-Type": "application/json"}, data=response_msg)


    # ------------------------------------------------------------------------- #
    # Handles a Facebook GET request
    # ------------------------------------------------------------------------- #
    # request : the GET request that was received
    # ------------------------------------------------------------------------- #
    # return  : HttpResponse
    # ------------------------------------------------------------------------- #
    def handleGetRequest ( self, request ):

        if request.GET['hub.verify_token'] == ApplicationKey.getApplicationToken ( ):
            return HttpResponse ( request.GET[ 'hub.challenge' ] )
        else:
            #todo error handling
            print ("Error in authentication")
            return HttpResponse ( "Error in authentication" )


    # ------------------------------------------------------------------------- #
    # Handles a Facebook POST request
    # ------------------------------------------------------------------------- #
    # request : the POST request that was received
    # ------------------------------------------------------------------------- #
    # return  : HttpResponse
    # ------------------------------------------------------------------------- #
    def handlePostRequest ( self, request ):

        facebookData = FacebookData ( request )

        if ( facebookData.requestType == MessageType.MESSAGE ):
            self.processMessage ( facebookData, request.session )
        elif ( facebookData.requestType == MessageType.POSTBACK ):
            self.processPostback ( facebookData, request.session )
        # todo handle delivery type messages?


    # ------------------------------------------------------------------------- #
    # Retrieves a Facebook user's first name
    # ------------------------------------------------------------------------- #
    # facebookId : the ID of the user whose first name is being requested
    # ------------------------------------------------------------------------- #
    # return  : user's first name
    # ------------------------------------------------------------------------- #
    def getUserFirstName ( self, facebookId ):
        response = requests.get ( 'https://graph.facebook.com/v2.6/' + facebookId + '?access_token=' + ApplicationKey.applicationKey )
        responseData = response.json ( )
        if ( 'first_name' in responseData ):
            return responseData[ 'first_name' ]
        else:
            # todo error handling
            return None


    # ------------------------------------------------------------------------- #
    # STATIC METHODS
    # ------------------------------------------------------------------------- #
    def processMessage ( self, facebookData, session ):
        if ( 'facebookId' in session ):
            # continue the conversation
            nextMessage = "What's the best email address for you?"
            self.sendMessage ( facebookData.facebookId, nextMessage )

        else:
            # create session and say hi
            session[ 'facebookId' ] = facebookData.facebookId
            # todo set expiration data
            welcomeMessage = ( "Hello, " + self.getUserFirstName ( facebookData.facebookId ) + "! Thanks for "
                               "choosing <PRACTICE NAME>. I'm here to help you schedule your free LASIK consultation. "
                               "I just need a couple more pieces of information. Let's get started!" )

            self.sendMessage( facebookData.facebookId, welcomeMessage )


    def processPostback ( self, facebookData, session ):
        return 1


