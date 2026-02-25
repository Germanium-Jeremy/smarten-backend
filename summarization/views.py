from django.http import JsonResponse
from django.db.models import Avg, Max
from django.utils import timezone
from datetime import datetime, time as dt_time, timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from sensors.models import UserSensors
from .models import SensorData

# Create your views here.

def get_average_data(user, start_time, end_time, period_type):
     """Helper function to get average data for a given time period for the authenticated user"""
     # Get all user-sensor mappings for the user
     user_sensors = UserSensors.objects.filter(user=user)
     if not user_sensors.exists():
          return JsonResponse({
               'period_type': period_type,
               'start_time': start_time.isoformat(),
               'end_time': end_time.isoformat(),
               'sensor_count': 0,
               'average_flow_rate': 0,
               'total_volume': 0,
               'sensor_data': []
          })

     # Get all SensorData for these user sensors in the time period
     sensor_data = SensorData.objects.filter(
          sensor__in=user_sensors,
          timestamp__gte=start_time,
          timestamp__lt=end_time
     )

     # Calculate averages and max volume
     averages = sensor_data.aggregate(
          avg_flow_rate=Avg('flow_rate'),
          max_volume=Max('volume')
     )

     # Get data per sensor
     sensor_metrics = []
     for user_sensor in user_sensors:
          sensor_avg = SensorData.objects.filter(
               sensor=user_sensor,
               timestamp__gte=start_time,
               timestamp__lt=end_time
          ).aggregate(
               avg_flow_rate=Avg('flow_rate'),
               max_volume=Max('volume')
          )
          sensor_metrics.append({
               'user_sensor_id': user_sensor.id,
               'sensor_id': user_sensor.sensor.id if hasattr(user_sensor, 'sensor') else None,
               'sensor_mac_address': user_sensor.sensor.mac_address if hasattr(user_sensor, 'sensor') else None,
               'average_flow_rate': sensor_avg['avg_flow_rate'] or 0,
               'total_volume': sensor_avg['max_volume'] or 0
          })

     return JsonResponse({
          'period_type': period_type,
          'start_time': start_time.isoformat(),
          'end_time': end_time.isoformat(),
          'sensor_count': user_sensors.count(),
          'average_flow_rate': averages['avg_flow_rate'] or 0,
          'total_volume': averages['max_volume'] or 0,
          'sensor_data': sensor_metrics
     })


# GET AVERAGE DATA FOR PASSED HOURS
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def passed_hourd_average(request, hour):
     """Get average data for a passed hours of the day (0-23) for all user's sensors"""
     try:
          user = request.user
          now = timezone.now()
          target_date = now.date()
          start_time = timezone.make_aware(datetime.combine(target_date, dt_time(hour=0)))
          end_time = timezone.make_aware(datetime.combine(target_date, dt_time(hour=hour)))
          return get_average_data(user, start_time, end_time, 'hourly')
     except Exception as e:
          return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# GET AVERAGE HOURLY DATA
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hourly_average(request, hour):
     """Get average data for a specific hour (0-23) for all user's sensors"""
     try:
          user = request.user
          now = timezone.now()
          target_date = now.date()
          start_time = timezone.make_aware(datetime.combine(target_date, dt_time(hour=hour)))
          end_time = start_time + timedelta(hours=1)
          return get_average_data(user, start_time, end_time, 'hourly')
     except Exception as e:
          return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# GET AVERAGE DAILY DATA
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def daily_average(request, year, month, day):
     """Get average data for a specific day for all user's sensors"""
     try:
          user = request.user
          start_time = timezone.make_aware(datetime(year, month, day))
          end_time = start_time + timedelta(days=1)
          return get_average_data(user, start_time, end_time, 'daily')
     except Exception as e:
          return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# GET AVERAGE MONTHLY DATA
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_average(request, year, month):
     """Get average data for a specific month for all user's sensors"""
     try:
          user = request.user
          if month == 12:
               next_month = 1
               next_year = year + 1
          else:
               next_month = month + 1
               next_year = year
          start_time = timezone.make_aware(datetime(year, month, 1))
          end_time = timezone.make_aware(datetime(next_year, next_month, 1))
          return get_average_data(user, start_time, end_time, 'monthly')
     except Exception as e:
          return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# GET AVERAGE YEARLY DATA
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def yearly_average(request, year):
     """Get average data for a specific year for all user's sensors"""
     try:
          user = request.user
          start_time = timezone.make_aware(datetime(year, 1, 1))
          end_time = timezone.make_aware(datetime(year + 1, 1, 1))
          return get_average_data(user, start_time, end_time, 'yearly')
     except Exception as e:
          return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)