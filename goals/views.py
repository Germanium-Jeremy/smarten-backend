from rest_framework.decorators import api_view, permission_classes
from .models import Goals
from authentication.models import UserModel as User
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework import status
import json


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def goals_get_goals(request):
     user_id = request.user.pk
     try:
          goals = Goals.objects.get(user=user_id)
          print(f"User: {goals}")
          return JsonResponse({'message': 'Goals fetched successfully', 'goals': goals.to_dict()}, status=200)
     except Goals.DoesNotExist:
          default_goals = {
               'daily_goals': 0.0,
               'monthly_goals': 0.0,
               'conservation_goal': [],
               'cost_goal': 0.0,
          }
          return JsonResponse({'message': 'Goals not found for this user.', 'goals': default_goals}, status=200)
     except Exception as e:
          print(str(e))
          return JsonResponse({ "error": str(e) }, status=500)
     

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def goals_set_goals(request):
     user_id = request.user.pk
     try:
          data = request.data if hasattr(request, 'data') else JSONParser().parse(request)
          # Double check user exists in DB
          from authentication.models import UserModel
          try:
               user_obj = UserModel.objects.get(user_id=user_id)
               print(f"User found: {user_obj}")
          except UserModel.DoesNotExist:
               return JsonResponse({'error': 'User not found.'}, status=404)

          # Extract goal fields from data
          daily_goals = data.get('daily_goals', 0.0)
          monthly_goals = data.get('monthly_goals', 0.0)
          conservation_goal = data.get('conservation_goal', [])
          cost_goal = data.get('cost_goal', 0.0)

          # Create or update the user's goals
          goals_obj, created = Goals.objects.update_or_create(
               user=user_obj,
               defaults={
                    'daily_goals': daily_goals,
                    'monthly_goals': monthly_goals,
                    'conservation_goal': conservation_goal,
                    'cost_goal': cost_goal,
               }
          )
          status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
          return JsonResponse({'message': 'Goals set successfully', 'goals': goals_obj.to_dict()}, status=status_code)
     except Exception as e:
          print(f"Error in set_goals: {e}")
          return JsonResponse({'error': str(e)}, status=500)