import json
import requests
from enum import Enum
from . import ApplicationKey
from django.http import HttpResponse
from pprint import pprint
from .models import client, facebookuser, lead, availability
from django.core.validators import validate_email, RegexValidator
from django.core.exceptions import ValidationError


class MessageType(Enum):
    MESSAGE = 0
    POSTBACK = 1
    DELIVERY = 2


class FacebookData:
    page_id = None
    update_time = None
    facebook_id = None
    first_name = None
    text = None
    payload = None
    request_type = None

    def __init__(self, data, page_id, update_time):

        self.page_id = page_id
        self.update_time = update_time

        if 'sender' in data:
            self.facebook_id = data['sender']['id']

        if 'message' in data:
            self.request_type = MessageType.MESSAGE
            self.text = data['message']['text']

        elif 'postback' in data:
            self.request_type = MessageType.POSTBACK
            self.payload = data['postback']['payload']


# This class serves as the interface to the Facebook Messenger API
class FacebookComm:
    # ------------------------------------------------------------------------- #
    # Sends a POST message to Facebook Messenger
    # ------------------------------------------------------------------------- #
    # facebookId : the ID of the user to which we're sending the message
    # message    : the message to send
    # ------------------------------------------------------------------------- #
    # return     : n/a
    # ------------------------------------------------------------------------- #
    @staticmethod
    def send_message(facebook_id, message):

        # todo Eventually I'll need to fetch the pageKey from the database as each will be unique to a customer
        page_key = ApplicationKey.application_key  # todo error handling if this is doesn't get set
        post_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + page_key
        response_msg = json.dumps({"recipient": {"id": facebook_id}, "message": {"text": message}})

        # todo: error handling
        print("Sending message:")
        print(message)
        requests.post(post_url, headers={"Content-Type": "application/json"}, data=response_msg)

    # ------------------------------------------------------------------------- #
    # Handles a Facebook GET request
    # ------------------------------------------------------------------------- #
    # request : the GET request that was received
    # ------------------------------------------------------------------------- #
    # return  : HttpResponse
    # ------------------------------------------------------------------------- #
    @staticmethod
    def handle_get_request(request):
        print("Handling GET request")
        if request.GET['hub.verify_token'] == ApplicationKey.get_application_token():
            return HttpResponse(request.GET['hub.challenge'])
        else:
            # todo error handling
            print("Error in authentication")
            return HttpResponse("Error in authentication")

    # ------------------------------------------------------------------------- #
    # Handles a Facebook POST request
    # ------------------------------------------------------------------------- #
    # request : the POST request that was received
    # ------------------------------------------------------------------------- #
    # return  : HttpResponse
    # ------------------------------------------------------------------------- #
    def handle_post_request(self, request):
        print("FacebookComm.handlePostRequest")

        # the format for incoming Facebook messages is the following:
        #   "object" : "page"
        #   "entry"  : [ array of entry objects ]
        #       "entry" : { "page id", "time of update", [ array of messaging objects ] }
        #           "messaging" : { "sender id", "recipient id", ... (callback specific fields) }

        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in request['entry']:
            page_id = entry['id']
            update_time = entry['time']

            for message in entry['messaging']:
                print(message)
                facebook_data = FacebookData(message, page_id, update_time)

                if facebook_data.request_type == MessageType.MESSAGE:
                    print("Processing message")
                    self.process_message(facebook_data)

                elif facebook_data.request_type == MessageType.POSTBACK:
                    print("Processing postback")
                    self.process_postback(facebook_data)
                    # todo handle delivery type messages?

    # ------------------------------------------------------------------------- #
    # Retrieves a Facebook user's first name
    # ------------------------------------------------------------------------- #
    # facebookId : the ID of the user whose first name is being requested
    # ------------------------------------------------------------------------- #
    # return  : user's first name
    # ------------------------------------------------------------------------- #
    @staticmethod
    def get_user_first_name(facebook_id):
        print("fetching first name")
        response = requests.get('https://graph.facebook.com/v2.6/' +
                                str(facebook_id) + '?access_token=' +
                                ApplicationKey.application_key)

        response_data = response.json()

        pprint(response_data)

        if 'first_name' in response_data:
            return response_data['first_name']
        else:
            # todo error handling
            return None

    @staticmethod
    def format_phone_number(phone_number):
        formatted_number = ''
        for char in phone_number:
            if char.isdigit():
                formatted_number += str(char)

        return formatted_number

    # ------------------------------------------------------------------------- #
    # STATIC METHODS
    # ------------------------------------------------------------------------- #
    def process_message(self, facebook_data):

        try:
            user = facebookuser.objects.get(facebook_id=facebook_data.facebook_id)
        except facebookuser.DoesNotExist:
            user = None

        # IF USER IN DATABASE
        if user is not None:
            print("We have this user. Checking for email")

            ####################
            # FOR DEV PURPOSES #
            ####################
            if facebook_data.text == 'delete':
                user.delete()
                self.send_message(facebook_data.facebook_id, "DELETED")
                return

            # IF EMAIL IS IN DATABASE
            if user.email_address is not None:
                print("We have email. Checking for phone number")

                if user.phone_number is not None:
                    print("We have phone number. Checking for consultation")

                    try:
                        practice = client.objects.get(facebook_page_id=facebook_data.page_id)
                    except client.DoesNotExist:
                        print("We got a request with a page ID that's not in our database")
                        return

                    # IF THEY HAVE AN APPOINTMENT BOOKED
                    consultation = lead.objects.filter(facebook_user=user.id,
                                                       practice=practice.id)

                    if len(consultation) == 1:
                        print("We have a scheduled consultation")
                        # IF THE CONSULTATION IS IN THE PAST
                        # IGNORE ??
                        # ELSE
                        # ASK IF THEY WOULD LIKE TO RESCHEDULE
                        message = "I see you already have a scheduled consultation on <date/time>"
                        self.send_message(facebook_data.facebook_id, message)
                    else:
                        print("We don't have a scheduled consultation yet")
                        self.schedule_consultation(facebook_data, True)

                else:
                    print("We don't have phone number. See if that's what they sent")
                    # SAVE THE PHONE NUMBER AND LET THEM KNOW WE MIGHT TEXT THEM. SEE IF THAT'S OK
                    if self.phone_number_is_valid(facebook_data.text):
                        user.phone_number = self.format_phone_number(facebook_data.text)
                        user.save()

                        message = "Great! As a side note, we sometimes send text messages for " \
                                  "reminders and such. Are you good with texting?"
                        button_payload = [{"type": "postback", "title": "YES", "payload": "YES TEXTING"},
                                          {"type": "postback", "title": "NO", "payload": "NO TEXTING"}]

                        self.send_buttons(facebook_data.facebook_id, message, button_payload)

                    else:
                        message = "Sorry, that doesn't appear to be a valid phone number. " \
                                  "Can you please re-enter it? (xxx-xxx-xxxx)"
                        self.send_message(facebook_data.facebook_id, message)

            else:
                print("We don't have email. See if that's what they sent")
                # SEE IF THEY PROVIDED A VALID EMAIL ADDRESS
                if self.email_is_valid(facebook_data.text):
                    # SAVE THE EMAIL AND REQUEST PHONE NUMBER
                    user.email_address = facebook_data.text
                    user.save()

                    message = "Perfect! And what's your cell phone number?"
                    self.send_message(facebook_data.facebook_id, message)
                else:
                    # ASK FOR THE EMAIL AGAIN
                    facebook_data.payload = "OK"
                    self.process_postback(facebook_data)
        else:
            # SEND GREETING
            print("Saving new user and sending greeting")
            user = facebookuser(facebook_id=facebook_data.facebook_id)

            facebook_data.first_name = self.get_user_first_name(facebook_data.facebook_id)
            if facebook_data.first_name is not None:
                user.first_name = facebook_data.first_name

            user.save()
            self.send_greeting(facebook_data)

    def send_greeting(self, facebook_data):

        try:
            practice_name = client.objects.get(facebook_page_id=facebook_data.page_id).practice_name
        except client.DoesNotExist:
            practice_name = "<PRACTICE NAME>"

        if facebook_data.first_name is not None:
            intro = "Hi, " + facebook_data.first_name + "!"
        else:
            intro = "Hey there!"

        # todo fetch the <PRACTICE NAME> based on the page id
        welcome_message = (intro + " Thanks for choosing " + practice_name +
                           ". I'm here to help you schedule your free LASIK consultation. "
                           "I just need a couple more pieces of information. Let's get started!")

        button_payload = [{"type": "postback", "title": "OK", "payload": "OK"}]

        self.send_buttons(facebook_data.facebook_id, welcome_message, button_payload)

    @staticmethod
    def send_buttons(facebook_id, message, payload):
        print("Sending callback buttons")
        post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + ApplicationKey.application_key
        callback_message = json.dumps({"recipient": {"id": facebook_id}, "message": {
            "attachment": {"type": "template",
                           "payload": {"template_type": "button", "text": message, "buttons": payload}
                           }}})

        print("Button Message: ", callback_message)
        requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=callback_message)
        # todo error handling

    def process_postback(self, facebook_data):
        if facebook_data.payload == "OK":
            print("Received 'ok' postback")
            message = "What's the best email address for you?"

        elif facebook_data.payload == "YES TEXTING":
            print("User is ok with texting")

            user = facebookuser.objects.get(facebook_id=facebook_data.facebook_id)
            user.ok_to_text = True
            user.save()
            message = "Perfect! Now that I have your info, let's figure out " \
                      "the day and time that works best for you. The appointment " \
                      "is free and it lasts about 1 hour."
            self.send_message(facebook_data.facebook_id, message)
            self.schedule_consultation(facebook_data, False)
            message = None

        elif facebook_data.payload == "NO TEXTING":
            user = facebookuser.objects.get(facebook_id=facebook_data.facebook_id)
            user.ok_to_text = False
            user.save()
            message = "Sounds good, we'll give you a call instead! Now that I have " \
                      "your info, let's figure out the day and time that works best " \
                      "for you. The appointment is free and it lasts about 1 hour."
            self.send_message(facebook_data.facebook_id, message)
            self.schedule_consultation(facebook_data, False)
            message = None

        elif facebook_data.payload == "later":
            print("Received 'later' postback")
            message = "Sounds good! Just stop back by when you want to schedule your free consultation"

        elif facebook_data.payload == "START":
            print("Someone pushed the 'Get Started' button")
            self.process_message(facebook_data)
            message = None

        else:
            message = None

        if message is not None:
            self.send_message(facebook_data.facebook_id, message)


    @staticmethod
    def get_appt_options(page_id):
        print("fetching appointment options")
        client_availability = availability.objects.filter(practice=client.objects.get(facebook_page_id=page_id).pk)
        button_payload = []
        current_count = 0

        if len(client_availability) > 0:
            print("iterating through client availability options")
            for option in client_availability:
                schedule_text = str(option.day_of_the_week) + " between " + \
                                str(option.start_time) + " and " + str(option.end_time)

                button_payload.append({"type": "postback",
                                       "title": schedule_text,
                                       "payload": str(current_count)})
                current_count += 1

            button_payload.append({"type": "postback",
                                   "title": "None of these work for me",
                                   "payload": str(current_count)})

        else:
            print("no availability entries for this client")
            button_payload = None

        return button_payload

    def schedule_consultation(self, facebook_data, continued_convo):
        print("scheduling consultation")
        if continued_convo is True:
            message = "Shall we continue scheduling your consultation? " \
                      "Again, the appointment is free and lasts about 1 hour. " \
                      "Which of these options works best for you?"
        else:
            message = "Which of these options works best for you?"

        appt_option_payload = FacebookComm.get_appt_options(facebook_data.page_id)

        if appt_option_payload is not None:
            print("Payload:", appt_option_payload)
            self.send_buttons(facebook_data.facebook_id, message, appt_option_payload)
        else:
            print("No appointment options.")
            message = "Sorry, it doesn't look as though " + \
                      client.objects.get(facebook_page_id = facebook_data.page_id).practice_name + \
                      " has any consultation times available. I will talk with them and have them reach " \
                      "out to you personally to schedule something. Thanks!"

            self.send_message(facebook_data.facebook_id, message)


    @staticmethod
    def phone_number_is_valid(text):
        phone_number_regex = r']*([0-9]{3}){1}[).\- ]*([0-9]{3}){1}[.\- ]*([0-9]{4}){1}$'
        regex_validator = RegexValidator(phone_number_regex)
        try:
            regex_validator(text)
            return True
        except ValidationError:
            return False

    @staticmethod
    def email_is_valid(text):
        try:
            validate_email(text)
            return True
        except ValidationError:
            return False
