from django.contrib import admin
from LasikBot import models

# Register your models here.
admin.site.register(models.client)
admin.site.register(models.lead)
admin.site.register(models.facebookuser)
admin.site.register(models.availability)
