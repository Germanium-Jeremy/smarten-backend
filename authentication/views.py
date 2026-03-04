import json, shutil, os
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.conf import settings
from django.core.files import File
from django.urls import reverse
from rest_framework.decorators import api_view
from .models import User
from smarten.utils import send_templated_email


# Create your views here.
@api_view(['POST', 'GET'])
def authentication_register(request):
     try:
          signupData = json.loads(request.body)
          print(f"Signup Data received: {signupData}")

          required_fields = ["first_name", "last_name", "email", "password", "phone"]

          # Validate required fields
          for field in required_fields:
               if field not in signupData or not signupData[field]:
                    return JsonResponse({'error': f'{field} is required'}, status=400)
               
          first_name = signupData['first_name']
          last_name = signupData['last_name']
          email = signupData['email']
          password = signupData['password']
          phone = signupData['phone']

          # Check if email already exists
          if User.objects.filter(email=email).exists():
               return JsonResponse({'error': 'Email already exists'}, status=400)
          
          # Assign random default profile image
          default_svg = User.get_random_default_image()
          svg_basename = os.path.basename(default_svg)
          print(f"Selected default SVG: {svg_basename}")
          dest_dir = os.path.join(settings.MEDIA_ROOT, 'profile_images')
          os.makedirs(dest_dir, exist_ok=True)
          dest_path = os.path.join(dest_dir, svg_basename)
          shutil.copyfile(default_svg, dest_path)

          # Create user with profile_image
          with open(dest_path, 'rb') as img_file:
               user = User(email=email, phone=phone, verified=False)
               user.set_password(password)  # Hash the password
               user.profile_image = svg_basename  # Set the profile image path
               user.save()  # Save the user

          # Generate access and refresh tokens
          refresh_token = RefreshToken.for_user(user)
          access_token = str(refresh_token.access_token)

          # Use the same token for verification
          verification_url = request.build_absolute_uri(reverse('verify_email') + f'?token={access_token}')
          send_templated_email(
               subject='Verify your email',
               recipient=user.email,
               template_name='verification_email.txt',
               context={
                    'first_name': first_name,
                    'last_name': last_name,
                    'verification_link': verification_url,
               }
          )

          # Send in-app notification via channels
          # send_user_notification(user.id, "Account Created", "Your account was successfully registered.")

          resp = JsonResponse({ 'message': 'User registered successfully', 'token': str(access_token), 'refresh': str(refresh_token)}, status=201)

          return resp

     except Exception as e:
          print(e)
          return JsonResponse({'error': str(e)}, status=500)
