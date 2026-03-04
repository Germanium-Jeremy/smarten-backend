from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
import random

class User(models.Model):     
     # Fields
     email = models.EmailField(unique=True, null=False, blank=False)
     recovery_email = models.EmailField(null=True, blank=True)
     password = models.CharField(max_length=128, null=False, blank=False)
     verified = models.BooleanField(default=False)
     phone = models.CharField(max_length=15, blank=False, null=False)
     created_at = models.DateTimeField(auto_now_add=True)
     last_login = models.DateTimeField(null=True, blank=True)
     profile_image = models.CharField(max_length=255, default='', blank=True)
     access_token = models.CharField(max_length=255, null=True, blank=True)
     refresh_token = models.CharField(max_length=255, null=True, blank=True)
     email_verification_code = models.CharField(max_length=6, null=True, blank=True)
     password_reset_code = models.CharField(max_length=6, null=True, blank=True)
     phone_verification_code = models.CharField(max_length=6, null=True, blank=True)
     phone_verified = models.BooleanField(default=False)

     # Methods

     def set_password(self, raw_password):
          """Hashes the password."""
          self.password = make_password(raw_password)

     def check_password(self, raw_password):
          """Checks if the provided password matches the hashed password."""
          return check_password(raw_password, self.password)
     
     @staticmethod
     def get_random_default_image():
          """Returns a random default image path."""
          choices = [
               '/media/images/default1.svg',
               '/media/images/default2.svg',
               '/media/images/default3.svg',
          ]
          return random.choice(choices)

     def save(self, *args, **kwargs):
          """Override save to handle any additional logic if needed."""
          super().save(*args, **kwargs)
