import json
import requests
from enum import Enum

MessageType = Enum ( 'message', 'delivery', 'postback' )

# This class serves as the interface to the Facebook Messenger API
class facebookComm ( ):

    # ------------------------------------------------------------------------- #
    # Sends a POST message to facebook messenger
    # ------------------------------------------------------------------------- #
    # facebookId : the ID of the user to which we're sending the message
    # pageKey    : the app key for the page to which we're sending the message
    # message    : the message to send
    # ------------------------------------------------------------------------- #
    # return
    # ------------------------------------------------------------------------- #
    def sendMessage ( self, facebookID, pageKey, message ):

        postUrl = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + pageKey
        response_msg = json.dumps ( { "recipient": { "id": facebookID }, "message": { "text": message } } )

        # todo: error handling
        requests.post(postUrl, headers={"Content-Type": "application/json"}, data=response_msg)