from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User

# Create your models here.
class GoogleUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255, null=True)
    is_site_generated = models.BooleanField(default=False)
    guser_id = models.CharField(max_length=255, null=True)
