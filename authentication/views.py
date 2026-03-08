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
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes


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
          
          # Create user object
          user = User(
               first_name=first_name,
               last_name=last_name,
               email=email,
               phone=phone,
               verified=False
          )

          # Assign random default profile image if possible
          default_svg = User.get_random_default_image()
          if default_svg:
               with open(default_svg, 'rb') as f:
                    user.profile_image.save(os.path.basename(default_svg), File(f), save=False)
          
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

          # Serialize user with context for absolute URLs
          user_data = UserSerializer(user, context={'request': request}).data
          resp = JsonResponse({ 
               'message': 'User registered successfully', 
               'token': str(access_token), 
               'refresh': str(refresh_token),
               'user': user_data
          }, status=201)

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

          # Serialize user with context for absolute URLs
          user_data = UserSerializer(user, context={'request': request}).data
          return JsonResponse({
               'message': 'Login successful',
               'token': access,
               'refresh': str(refresh),
               'user': user_data
          }, status=200)
     except Exception as e:
          print(e)
          return JsonResponse({'error': str(e)}, status=500)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def authentication_update_profile(request):
     try:
          user = request.user
          data = json.loads(request.body)
          
          user.first_name = data.get('first_name', user.first_name)
          user.last_name = data.get('last_name', user.last_name)
          
          new_email = data.get('email')
          if new_email and new_email != user.email:
               if User.objects.filter(email=new_email).exclude(user_id=user.user_id).exists():
                    return JsonResponse({'error': 'Email already in use by another account'}, status=400)
               user.email = new_email
               
          user.save()
          
          serializer = UserSerializer(user, context={'request': request})
          return JsonResponse(serializer.data, status=200)
          
     except Exception as e:
          print(f"Error updating profile: {e}")
          return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def authentication_profile_change(request):
     try:
          user = request.user
          if 'profile_image' not in request.FILES:
               return JsonResponse({'error': 'No image file provided'}, status=400)
          
          image_file = request.FILES['profile_image']
          
          # This will automatically upload to Cloudinary if configured
          user.profile_image.save(image_file.name, image_file, save=True)
          
          # Return full URL
          profile_image_url = request.build_absolute_uri(user.profile_image.url) if not settings.DEBUG else user.profile_image.url
          if settings.DEBUG and not profile_image_url.startswith('http'):
               profile_image_url = request.build_absolute_uri(profile_image_url)

          return JsonResponse({
               'message': 'Profile image updated successfully',
               'profile_image': profile_image_url
          }, status=200)
          
     except Exception as e:
          print(f"Error uploading image: {e}")
          return JsonResponse({'error': str(e)}, status=500)
