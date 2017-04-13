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

        # this is not needed if small_image is created at set_image
    def save(self, *args, **kwargs):
        if not BlogSettings.objects.filter(user=self.user).exists():
            blogsettings = BlogSettings(user=self.user)
            blogsettings.save()
        super(GoogleUser, self).save(*args, **kwargs)


class BlogSettings(models.Model):
    user = models.OneToOneField(User)
    title = models.CharField(max_length=255, null=True)
    subtitle = models.TextField(null=True)
    description = models.TextField(null=True)
    ga_id = models.CharField(max_length=255, null=True)

