from django.db import models
from authentication.models import UserModel as User

# Create your models here.
class Sensor(models.Model):
     mac_address = models.CharField(null=False, unique=True)
     status = models.CharField(max_length=100, default='registered')

class UserSensors(models.Model):
     user = models.ForeignKey(User, on_delete=models.CASCADE)
     sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)

class SensorCommand(models.Model):
     sensor = models.ForeignKey(UserSensors, on_delete=models.CASCADE, related_name='commands')
     command = models.CharField(max_length=10)  # 'ON' or 'OFF'
     timestamp = models.DateTimeField(auto_now_add=True)
     status = models.CharField(max_length=20, default='PENDING')  # PENDING, SENT, FAILED
     response = models.TextField(null=True, blank=True)

     def __str__(self):
          return f"{self.sensor.mac_address} - {self.command} at {self.timestamp}"

     def to_dict(self):
          return {
               'id': self.id,
               'sensor_id': self.sensor_id,
               'command': self.command,
               'timestamp': self.timestamp.isoformat(),
               'status': self.status,
               'response': self.response
          }