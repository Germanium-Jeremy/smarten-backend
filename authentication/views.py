import json, shutil, os
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.conf import settings
from django.core.files import File
from django.urls import reverse
from rest_framework.decorators import api_view
from .models import UserModel as User
from .serializers import RegisterSerializer, UserSerializer
from smarten.utils import send_templated_email


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
          if default_svg:
               svg_basename = os.path.basename(default_svg)
               print(f"Selected default SVG: {svg_basename}")
               dest_dir = os.path.join(settings.MEDIA_ROOT, 'profile_images')
               os.makedirs(dest_dir, exist_ok=True)
               dest_path = os.path.join(dest_dir, svg_basename)
               if not os.path.exists(dest_path):
                    shutil.copyfile(default_svg, dest_path)
               profile_image_name = svg_basename
          else:
               print("No default SVG found in static/images. Skipping profile image assignment.")
               profile_image_name = ''

          # Create user with profile_image
          user = User(
               first_name=first_name,
               last_name=last_name,
               email=email,
               phone=phone,
               verified=False,
               profile_image=profile_image_name
          )
          user.set_password(password)  # Hash the password
          user.save()  # Save the user

          # Generate access and refresh tokens
          refresh_token = RefreshToken.for_user(user)
          access_token = str(refresh_token.access_token)

          # Use the same token for verification
          verification_url = request.build_absolute_uri(reverse('verify_email') + f'?token={access_token}')
          # delete_link = request.build_absolute_uri(reverse('delete_account') + f'?token={access_token}')

          send_templated_email(
               subject='Verify your email',
               recipient=user.email,
               template_name='emails/verification_email.html',
               context={
                    'first_name': first_name,
                    'last_name': last_name,
                    'verification_link': verification_url
                    # 'delete_link': delete_link
               }
          )

          resp = JsonResponse({ 'message': 'User registered successfully', 'token': str(access_token), 'refresh': str(refresh_token)}, status=201)

          return resp

     except Exception as e:
          print(e)
          return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def authentication_verify_email(request, token=None):
     token = request.GET.get('token')
     if not token:
          return render(request, 'emails/verification_error.html', {'error_message': 'Verification token is missing from the URL.'}, status=400)

     try:
          # Decode the token to get the user ID
          access_token = AccessToken(token)
          user_id_uuid = access_token['user_id']  # Get the user ID from the token

          user = User.objects.get(user_id=user_id_uuid)
          if user.verified:
               return render(request, 'emails/verification_success.html')

          # Mark the user as verified
          user.verified = True
          user.save()

          return render(request, 'emails/verification_success.html')

     except Exception as e:
          print(e)
          return render(request, 'emails/verification_error.html', {'error_message': 'The verification link is invalid or has expired.'}, status=400)


@api_view(['POST'])
def authentication_login(request):
     try:
          data = json.loads(request.body)
          print("Login Data: ", data)
          email = data.get('email')
          password = data.get('password')
          if not email or not password:
               return JsonResponse({'error': 'Email and password required.'}, status=400)

          user = User.objects.filter(email=email).first()
          if not user:
               return JsonResponse({'error': 'Invalid email or password.'}, status=401)

          if not user.check_password(password):
               return JsonResponse({'error': 'Invalid email or password.'}, status=401)

          print(f"User {user.user_id} authenticated successfully.")

          user.last_login = timezone.now()
          user.save()

          refresh = RefreshToken.for_user(user)
          access = str(refresh.access_token)

          return JsonResponse({
               'message': 'Login successful',
               'token': access,
               'refresh': str(refresh),
          }, status=200)
     except Exception as e:
          print(e)
          return JsonResponse({'error': str(e)}, status=500)
