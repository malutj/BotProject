import os

server = None

try:
    server = os.environ['SERVER']
except KeyError:
    # todo error
    print ("Unable to find 'SERVER' environment variable")

applicationKey   = None
applicationToken = None

botAlphaPageKey = ('EAARBuHDd8IYBAPVnZBaXX6kXbvwhHAADuMLXgZA5CXLMkNPvK5s0KzkzBl'
                   'jfFfUTut5K5DQeTKZBdEEY5bltZA601o5IrxUbMYL1xlBaLw9toCf329TPN'
                   'zcX9bdi6bpfowtQzeiYx5pXqm6amtHzfYNHGZAJR3IAGJPXZAfka7ZCQZDZD')

botTestPageKey = ('EAAY8WTjoQGkBAEQDhKm0dSO1ZAsKIZApTGZAJaxsZCoRO41ATCyrNMbsLQu'
                  'yMNNRXNJg34HZAkZCdtCRbSIXVdF6fdzqQazKCGuf3wrn0LUhW8wTIXTaMee'
                  'QNfQrltaeIXjirZAZC0ydZBH7ZADZAo37u7Ec2TUC2M3tbl5cvP5f1rZApwZDZD')

developmentToken = 'malutj'
releaseToken = 'a64f65974d0a43ab1302'

def getApplicationKey ( ):
    # todo error handling
    return applicationKey


def getApplicationToken ( ):
    # todo error handling
    return applicationToken


def configureForDevelopment ( ):
    global applicationKey
    global applicationToken
    global botTestPageKey
    global developmentToken

    applicationKey = botTestPageKey
    applicationToken = developmentToken
    print ( "Configured application for DEVELOPMENT mode" )


def configureForRelease ( ):
    global applicationKey
    global applicationToken
    global botTestPageKey
    global developmentToken

    applicationKey = botAlphaPageKey
    applicationToken = releaseToken
    print ( "Configured application for RELEASE mode" )


if ( server == "HEROKU" ):
    configureForRelease( )
else:
    configureForDevelopment( )




