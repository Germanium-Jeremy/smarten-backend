from django.urls import path
from .views import me

urlpatterns = [
     path('api/me/', me, name='me'),
]
