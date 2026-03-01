from rest_framework import serializers
from .models import User
import os

class RegisterSerializer(serializers.ModelSerializer):
     password = serializers.CharField(write_only=True, min_length=8)

     class Meta:
          model = User
          fields = ('first_name', 'last_name', 'email', 'password', 'phone')

     def validate_email(self, value):
          if User.objects.filter(email__iexact=value).exists():
               raise serializers.ValidationError('Email already registered.')
          return value.lower()

     def create(self, validated_data):
          user = User(
               first_name=validated_data['first_name'],
               last_name=validated_data['last_name'],
               email=validated_data['email'],
               phone=validated_data['phone'],
          )
          user.set_password(validated_data['password'])
          basename = os.path.basename(User.get_random_default_image())
          user.profile_image = basename
          user.save()
          return user