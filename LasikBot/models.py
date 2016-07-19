from django.db import models


# Create your models here.
# todo remove any options that are already defaults (like unique probably defaults to False)
class FacebookUser(models.Model):
    def __str__ ( self ):
        return ( self.firstName + " [" + self.facebookId + "]" )
    
    facebook_id = models.CharField(max_length=100, null=False, blank=False, unique=True)
    first_name = models.CharField(max_length=25, null=True, blank=True, unique=False)
    # todo should I make the email field unique?
    email_address = models.EmailField(max_length=255, null=True, blank=True, unique=False)
    phone_number = models.CharField(max_length=10, null=True, blank=True, unique=False)


class Client(models.Model):
    
    def __str__ ( self ):
        return self.practiceName
    
    facebook_page_id = models.CharField(max_length=100, null=False, blank=False, unique=True)
    # todo should I make the practice name field unique?
    practice_name = models.CharField(max_length=100, null=False, blank=False, unique=False)
    client_email = models.EmailField(max_length=255, null=False, blank=False, unique=False)

    class Meta:
        ordering = 'practiceName'

        
class Lead(models.Model):
    facebook_user = models.ForeignKey(FacebookUser, null=False, blank=False, on_delete=models.CASCADE)
    practice = models.ForeignKey(Client, null=False, blank=False, on_delete=models.CASCADE)
    date_received = models.DateField(auto_now_add=True, null=False, blank=False)
    consultation_date = models.DateField(auto_now_add=False, null=True, blank=True)
    consultation_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = (('facebookUser', 'practice'),)


class Availability(models.Model):
    practice = models.ForeignKey(Client, null=False, blank=False, on_delete=models.CASCADE)
    day_of_the_week = models.CharField(max_length=10, null=False, blank=False, unique=False)
    start_time = models.TimeField(null=False, blank=False, unique=False)
    end_time = models.TimeField(null=False, blank=False, unique=False)
