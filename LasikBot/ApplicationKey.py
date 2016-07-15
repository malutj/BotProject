import os

class ApplicationKey ( ):

    server = None

    try:
        server = os.environ['SERVER']
    except KeyError:
        # todo error
        print ("Unable to find 'SERVER' environment variable")

    botAlphaPageKey = ( 'EAARBuHDd8IYBAPVnZBaXX6kXbvwhHAADuMLXgZA5CXLMkNPvK5s0KzkzBl'
                        'jfFfUTut5K5DQeTKZBdEEY5bltZA601o5IrxUbMYL1xlBaLw9toCf329TPN'
                        'zcX9bdi6bpfowtQzeiYx5pXqm6amtHzfYNHGZAJR3IAGJPXZAfka7ZCQZDZD' )

    botTestPageKey = ( 'EAAY8WTjoQGkBAEQDhKm0dSO1ZAsKIZApTGZAJaxsZCoRO41ATCyrNMbsLQu'
                       'yMNNRXNJg34HZAkZCdtCRbSIXVdF6fdzqQazKCGuf3wrn0LUhW8wTIXTaMee'
                       'QNfQrltaeIXjirZAZC0ydZBH7ZADZAo37u7Ec2TUC2M3tbl5cvP5f1rZApwZDZD' )

    developmentToken = 'malutj'
    releaseToken     = 'a64f65974d0a43ab1302'

    applicationKey   = None
    applicationToken = None

    def __init__ ( self ):
        if ( self.server == "HEROKU" ):
            self.configureForRelease( )
        else:
            self.configureForDevelopment( )


    def getApplicationKey ( self ):
        #todo error handling
        return self.applicationKey


    def getApplicationToken ( self ):
        #todo error handling
        return self.applicationToken


    # ------------------------------------------------------------------------- #
    # STATIC METHODS
    # ------------------------------------------------------------------------- #
    def configureForDevelopment ( self ):
        self.applicationKey = self.botTestPageKey
        self.applicationToken = self.developmentToken
        print ("Configured application for DEVELOPMENT mode")


    def configureForRelease ( self ):
        self.applicationKey = self.botAlphaPageKey
        self.applicationToken = self.releaseToken
        print ("Configured application for RELEASE mode")
    # ------------------------------------------------------------------------- #
