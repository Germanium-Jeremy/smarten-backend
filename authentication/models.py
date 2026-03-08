from django.conf import settings
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import random, os, uuid

class CustomUserManager(BaseUserManager):
     def create_user(self, email, password=None, **extra_fields):
          if not email:
               raise ValueError("The Email field must be set")
          email = self.normalize_email(email)
          user = self.model(email=email, **extra_fields)
          user.set_password(password)
          user.save(using=self._db)
          return user

     def create_superuser(self, email, password=None, **extra_fields):
          extra_fields.setdefault('is_staff', True)
          extra_fields.setdefault('is_superuser', True)
          return self.create_user(email, password, **extra_fields)

class UserModel(models.Model):
     user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
     first_name = models.CharField(max_length=30, help_text="User's first name")                
     last_name  = models.CharField(max_length=30, help_text="User's last name")          
     email = models.EmailField(unique=True, help_text="User's email address")
     password = models.CharField(max_length=128, help_text="Hashed password")
     recovery_email = models.EmailField(null=True, blank=True)
     verified = models.BooleanField(default=False)
     phone = models.CharField(max_length=15, help_text="User's phone number")
     created_at = models.DateTimeField(auto_now_add=True)
     last_login = models.DateTimeField(null=True, blank=True)
     profile_image = models.ImageField(upload_to='profile_images/', default='', blank=True)
     access_token = models.CharField(max_length=255, null=True, blank=True)
     refresh_token = models.CharField(max_length=255, null=True, blank=True)
     email_verification_code = models.CharField(max_length=6, null=True, blank=True)
     password_reset_code = models.CharField(max_length=6, null=True, blank=True)
     phone_verification_code = models.CharField(max_length=6, null=True, blank=True)
     phone_verified = models.BooleanField(default=False)

     is_active = models.BooleanField(default=True, help_text="Designates whether this user should be treated as active.")

     USERNAME_FIELD = 'email' 
     REQUIRED_FIELDS = ['first_name', 'last_name', 'phone', 'password']

     objects = CustomUserManager()

     def set_password(self, raw_password):
          self.password = make_password(raw_password)

     def check_password(self, raw_password):
          return check_password(raw_password, self.password)
     
     @property
     def is_active(self):
          # return self.verified
          return True

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
     
     def __str__(self):
          return f"{self.first_name} {self.last_name} ({self.user_id})"
     
     @property
     def is_authenticated(self):
          """
          Always True for real users (required by Django auth system).
          """
          return True
     
     @property
     def is_anonymous(self):
          """
          Always False for real users (distinguishes from AnonymousUser).
          """
          return False

     def save(self, *args, **kwargs):
          super().save(*args, **kwargs)