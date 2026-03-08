from rest_framework import serializers
from .models import UserModel as User
from django.core.files import File
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
          
          default_svg = User.get_random_default_image()
          if default_svg:
               with open(default_svg, 'rb') as f:
                    user.profile_image.save(os.path.basename(default_svg), File(f), save=False)
          
          user.save()
          return user
     
class UserSerializer(serializers.ModelSerializer):
     id = serializers.UUIDField(read_only=True)
     user_id = serializers.UUIDField(read_only=True)
     profile_image = serializers.SerializerMethodField()
     
     class Meta:
          model = User
          fields = ['id', 'user_id', 'first_name', 'last_name', 'email', 'phone', 'profile_image', 'verified']

     def get_profile_image(self, obj):
          if obj.profile_image:
               request = self.context.get('request')
               if request:
                    return request.build_absolute_uri(obj.profile_image.url)
               return obj.profile_image.url
          return None
