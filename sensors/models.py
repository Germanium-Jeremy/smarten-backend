from django.db import models
from authentication.models import UserModel as User

# Create your models here.
class Sensor(models.Model):
    mac_address = models.CharField(null=False, unique=True)
    status = models.CharField(max_length=100, default='registered')

class UserSensors(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)