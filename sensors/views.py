
import json
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Sensor, UserSensors
from authentication.models import UserModel as User

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sensors_register(request):
	try:
		data = request.data if hasattr(request, 'data') else json.loads(request.body)
		mac_address = data.get('mac_address')
		if not mac_address:
			return JsonResponse({'error': 'mac_address is required'}, status=400)
		if Sensor.objects.filter(mac_address=mac_address).exists():
			return JsonResponse({'error': 'Sensor with this mac_address already exists'}, status=400)
		sensor = Sensor.objects.create(mac_address=mac_address)
		return JsonResponse({'message': 'Sensor registered successfully', 'sensor_id': sensor.id}, status=201)
	except Exception as e:
		return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sensors_map(request):
	try:
		user = request.user
		data = request.data if hasattr(request, 'data') else json.loads(request.body)
		mac_address = data.get('mac_address')
		print("Sensor mac: ", mac_address)
		if not mac_address:
			return JsonResponse({'error': 'mac_address is required'}, status=400)
		# Check if sensor exists
		sensor = Sensor.objects.filter(mac_address=mac_address).first()
		if not sensor:
			return JsonResponse({'error': 'Sensor with this mac_address does not exist'}, status=404)
		# Check if mapping exists
		mapping = UserSensors.objects.filter(sensor=sensor).first()
		if mapping:
			if mapping.user == user:
				return JsonResponse({'message': 'Sensor already mapped to this user'}, status=200)
			else:
				return JsonResponse({'error': 'Sensor already mapped to another user'}, status=400)
		# Create mapping
		user_sensor = UserSensors.objects.create(
			sensor=sensor,
			user=user
		)
		return JsonResponse({'message': 'Sensor mapped to user successfully', 'sensor_id': sensor.id, 'user_id': str(user.user_id) if hasattr(user, 'user_id') else str(user.id)}, status=201)
	except User.DoesNotExist:
		return JsonResponse({'error': 'User not found'}, status=404)
	except Exception as e:
		print(f"Error mapping sensor: {str(e)}")
		return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sensors_listing(request):
	sensors = Sensor.objects.all().values('id', 'mac_address', 'status')
	return JsonResponse({'sensors': list(sensors)}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sensors_list_mappings(request):
	mappings = UserSensors.objects.select_related('user', 'sensor').all()
	result = []
	for mapping in mappings:
		result.append({
			'mapping_id': mapping.id,
			'sensor_id': mapping.sensor.id,
			'mac_address': mapping.sensor.mac_address,
			'status': mapping.sensor.status,
			'user_id': str(mapping.user.user_id) if hasattr(mapping.user, 'user_id') else str(mapping.user.id),
			'user_email': mapping.user.email
		})
	return JsonResponse({'mappings': result}, status=200)
