from django.urls import path
from .views import goals_get_goals, goals_set_goals

urlpatterns = [
    path('api/get-goals/', goals_get_goals, name='get_goals'),
    path('api/set-goals/', goals_set_goals, name='set_goals'),
]
