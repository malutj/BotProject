from django.db import models

# Create your models here.
class FacebookUser ( models.Model ):

    def __str__ ( self ):
        return ( self.firstName + " [" + self.facebookId + "]" )
    facebookId = models.CharField ( max_length = 100, null = False, blank = False, unique = True )
    firstName = models.CharField ( max_length = 25, null = True, blank = True, unique = False )
    # todo should I make the email field unique?
    emailAddress = models.EmailField ( max_length = 255, null = True, blank = True, unique = False )
    phoneNumber = models.CharField ( max_length = 10, null = True, blank = True, unique = False )


class Client ( models.Model ):

    def __str__ ( self ):
        return self.practiceName

    facebookPageId = models.CharField ( max_length = 100, null = False, blank = False, unique = True )
    # todo should I make the practice name field unique?
    practiceName = models.CharField ( max_length = 100, null = False, blank = False, unique = False )
    clientEmail = models.EmailField ( max_length = 255, null = False, blank = False, unique = False )


class Lead ( models.Model ):
    facebookUser = models.ForeignKey ( FacebookUser, null = False, blank = False, on_delete = models.CASCADE )
    practice = models.ForeignKey ( Client, null = False, blank = False, on_delete = models.CASCADE )
    dateReceived = models.DateField ( auto_now_add = True, null = False, blank = False )


class Availability ( models.Model ):
    practice = models.ForeignKey ( Client, null = False, blank = False, on_delete = models.CASCADE )
    dayOfTheWeek = models.CharField ( max_length = 10, null = False, blank = False, unique = False )
    startTime = models.TimeField ( null = False, blank = False, unique = False )
    endTime = models.TimeField ( null = False, blank = False, unique = False )


