import os

try:
    server = os.environ['SERVER']
except KeyError:
    # todo error
    server = None
    print("Unable to find 'SERVER' environment variable")

application_key = None
application_token = None

bot_alpha_page_key = ('EAARBuHDd8IYBAPVnZBaXX6kXbvwhHAADuMLXgZA5CXLMkNPvK5s0Kzkz'
                      'BljfFfUTut5K5DQeTKZBdEEY5bltZA601o5IrxUbMYL1xlBaLw9toCf32'
                      '9TPNzcX9bdi6bpfowtQzeiYx5pXqm6amtHzfYNHGZAJR3IAGJPXZAfka7ZCQZDZD')

bot_test_page_key = ('EAAY8WTjoQGkBAEQDhKm0dSO1ZAsKIZApTGZAJaxsZCoRO41ATCyrNMbsL'
                     'QuyMNNRXNJg34HZAkZCdtCRbSIXVdF6fdzqQazKCGuf3wrn0LUhW8wTIXT'
                     'aMeeQNfQrltaeIXjirZAZC0ydZBH7ZADZAo37u7Ec2TUC2M3tbl5cvP5f1rZApwZDZD')

development_token = 'malutj'
release_token = 'a64f65974d0a43ab1302'


def get_application_key():
    # todo error handling
    return application_key


def get_application_token():
    # todo error handling
    return application_token


def configure_for_development():
    global application_key
    global application_token
    global bot_test_page_key
    global development_token

    application_key = bot_test_page_key
    application_token = development_token
    print("Configured application for DEVELOPMENT mode")


def configure_for_release():
    global application_key
    global application_token
    global bot_test_page_key
    global development_token

    application_key = bot_alpha_page_key
    application_token = release_token
    print("Configured application for RELEASE mode")


if server == "HEROKU":
    configure_for_release()
else:
    configure_for_development()
