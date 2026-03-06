from django.urls import path
from .views import sensors_listing, sensors_list_mappings, sensors_map, sensors_register, sensors_commands, sensors_control

urlpatterns = [
	path('api/register-sensor/', sensors_register, name='register_sensor'),
	path('api/map-sensor/', sensors_map, name='map_sensor'),
	path('api/list-sensors/', sensors_listing, name='list_sensors'),
	path('api/list-mappings/', sensors_list_mappings, name='list_mappings'),
     path('api/sensor-command/<int:sensor_id>/', sensors_control, name='open_close_sensor'),
     path('api/sensor-history/<int:sensor_id>/', sensors_commands, name='History for sensor commands'),
]
