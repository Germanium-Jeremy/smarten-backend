from django.db import models
from authentication.models import UserModel as User

# Create your models here.
class Goals(models.Model):
     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
     daily_goals = models.FloatField(default=0.0)
     monthly_goals = models.FloatField(default=0.0)
     conservation_goal = models.JSONField(default=list)
     cost_goal = models.FloatField(default=0.0)

     def to_dict(self):
          return {
               'daily_goals': self.daily_goals,
               'monthly_goals': self.monthly_goals,
               'conservation_goal': self.conservation_goal,
               'cost_goal': self.cost_goal,
          }
