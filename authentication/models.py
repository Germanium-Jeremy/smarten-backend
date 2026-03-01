from django.conf import settings
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import random, os

class User(models.Model):
     first_name = models.CharField(max_length=30)                # new
     last_name  = models.CharField(max_length=30)                # new
     email = models.EmailField(unique=True)
     recovery_email = models.EmailField(null=True, blank=True)
     password = models.CharField(max_length=128)
     verified = models.BooleanField(default=False)
     phone = models.CharField(max_length=15)
     created_at = models.DateTimeField(auto_now_add=True)
     last_login = models.DateTimeField(null=True, blank=True)
     profile_image = models.CharField(max_length=255, default='', blank=True)
     access_token = models.CharField(max_length=255, null=True, blank=True)
     refresh_token = models.CharField(max_length=255, null=True, blank=True)
     email_verification_code = models.CharField(max_length=6, null=True, blank=True)
     password_reset_code = models.CharField(max_length=6, null=True, blank=True)
     phone_verification_code = models.CharField(max_length=6, null=True, blank=True)
     phone_verified = models.BooleanField(default=False)

     def set_password(self, raw_password):
          self.password = make_password(raw_password)

     def check_password(self, raw_password):
          return check_password(raw_password, self.password)

     @staticmethod
     def get_random_default_image():
          """
          Return the absolute path of one of the three SVGs that live
          in static/images/. If none exist, return None.
          """
          choices = [
               os.path.join(settings.BASE_DIR, 'media', 'images', 'default1.svg'),
               os.path.join(settings.BASE_DIR, 'media', 'images', 'default2.svg'),
               os.path.join(settings.BASE_DIR, 'media', 'images', 'default3.svg'),
          ]
          available = [f for f in choices if os.path.exists(f)]
          if available:
               return random.choice(available)
          return None

     def full_name(self):
          return f"{self.first_name} {self.last_name}"

     def save(self, *args, **kwargs):
          super().save(*args, **kwargs)