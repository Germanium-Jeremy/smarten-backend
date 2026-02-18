from django.urls import path
from .views import sensors_listing, sensors_list_mappings, sensors_map, sensors_register

urlpatterns = [
	path('api/register-sensor/', sensors_register, name='register_sensor'),
	path('api/map-sensor/', sensors_map, name='map_sensor'),
	path('api/list-sensors/', sensors_listing, name='list_sensors'),
	path('api/list-mappings/', sensors_list_mappings, name='list_mappings'),
]
