from django.urls import path
from .views import users_me, users_update_profile, users_profile_change

urlpatterns = [
     path('api/me/', users_me, name='users_me'),
     path('api/update_profile', users_update_profile, name='users_update_profile'),
     path('api/profile_change', users_profile_change, name='users_profile_change'),
]
