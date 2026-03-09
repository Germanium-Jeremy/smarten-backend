import json
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from authentication.models import UserModel as User
from authentication.serializers import UserSerializer
from sensors.models import UserSensors

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_me(request):
     try:
          user = request.user.pk

          # Fetch the user from the database
          user = User.objects.get(user_id=user)

          # Fetch connected sensors for this user
          sensors = UserSensors.objects.filter(user=user)
          connected_sensors = [
               {
                    'sensor_id': sensor.id,
                    'mac_address': sensor.sensor.mac_address if hasattr(sensor, 'sensor') else None,
                    'status': sensor.sensor.status
               }
               for sensor in sensors
          ] if sensors.exists() else []

          # Serialize user data with context for absolute URLs
          user_serializer = UserSerializer(user, context={'request': request})
          user_data = user_serializer.data
          user_data['connected_sensors'] = connected_sensors

          return JsonResponse(user_data, status=status.HTTP_200_OK)

     except User.DoesNotExist:
          return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

     except Exception as e:
          return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def users_update_profile(request):
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
def users_profile_change(request):
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
