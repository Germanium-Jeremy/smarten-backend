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
def me(request):
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