from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from .views import authentication_register, authentication_verify_email, authentication_login

urlpatterns = [
     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     path('api/register/', authentication_register, name='register'),
     path('api/login/', authentication_login, name='login'),
     path('api/verify-email/', authentication_verify_email, name='verify_email'),
]
