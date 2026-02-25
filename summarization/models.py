from django.db import models
from sensors.models import UserSensors

# Create your models here.
class SensorData(models.Model):
    sensor = models.ForeignKey(UserSensors, on_delete=models.CASCADE, related_name='data')
    flow_rate = models.FloatField()
    volume = models.FloatField()
    status = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)