
import json
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Sensor, UserSensors, SensorCommand
from mqtt_manager.mqtt_publisher import mqtt_publisher
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sensors_control(request, sensor_id):
     """
     Endpoint to control a specific sensor
     Expected JSON: {"command": "ON" | "OFF"}
     """
     user = request.user
     command = request.data.get('command', '').upper()
     if command not in ['ON', 'OFF']:
          return JsonResponse(
               {'error': 'Invalid command. Use "ON" or "OFF".'}, 
               status=status.HTTP_400_BAD_REQUEST
          )
     # Verify the sensor belongs to the user
     try:
          sensor = UserSensors.objects.get(id=sensor_id, user=user)
     except UserSensors.DoesNotExist:
          return JsonResponse(
               {'error': 'Sensor not found or access denied.'}, 
               status=status.HTTP_404_NOT_FOUND
          )
     # Create a command record
     cmd = SensorCommand.objects.create(
          sensor=sensor,
          command=command,
          status='PENDING'
     )
     try:
          # Send command via MQTT
          success, message = mqtt_publisher.publish_command(sensor.sensor.mac_address, command)
          if success:
               cmd.status = 'SENT'
               cmd.save()
               return JsonResponse({
                    'status': 'success',
                    'message': f'Command to turn {command} sent to sensor {sensor.sensor.mac_address}',
                    'command_id': cmd.id
               })
          else:
               cmd.status = 'FAILED'
               cmd.response = message
               cmd.save()
               return JsonResponse(
                    {'error': f'Failed to send command: {message}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
               )
     except Exception as e:
          cmd.status = 'FAILED'
          cmd.response = str(e)
          cmd.save()
          print(f"Error sending command to sensor {sensor_id}: {str(e)}")
          return JsonResponse(
               {'error': f'Failed to send command: {str(e)}'}, 
               status=status.HTTP_500_INTERNAL_SERVER_ERROR
          )
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sensors_commands(request, sensor_id):
     """
     Get command history for a sensor
     """
     try:
          user = request.user
          # Verify the sensor belongs to the user
          try:
               sensor = UserSensors.objects.get(id=sensor_id, user=user)
          except UserSensors.DoesNotExist:
               return JsonResponse(
                    {'error': 'Sensor not found or access denied.'}, 
                    status=status.HTTP_404_NOT_FOUND
               )
          # Get all commands for this sensor, newest first
          commands = SensorCommand.objects.filter(sensor=sensor).order_by('-timestamp')
          return JsonResponse({
               'sensor_id': sensor_id,
               'commands': [cmd.to_dict() for cmd in commands]
          })
     except Exception as e:
          print(f"Error getting sensor commands: {str(e)}")
          return JsonResponse(
               {'error': 'An error occurred while fetching command history'}, 
               status=status.HTTP_500_INTERNAL_SERVER_ERROR
          )