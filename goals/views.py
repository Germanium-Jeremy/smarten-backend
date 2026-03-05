from rest_framework.decorators import api_view, permission_classes
from .models import Goals
from authentication.models import UserModel as User
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
import json


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def goals_get_goals(request):
     user_id = request.user.pk
     try:
          goals = Goals.objects.get(user=user_id)
          print(f"User: {goals}")
          return JsonResponse({'message': 'This endpoint is under construction'}, status=200)
     except Goals.DoesNotExist:
          return JsonResponse({'message': 'Goals not found for this user.', 'goals': []}, status=200)
     except Exception as e:
          print(str(e))
          return JsonResponse({ "error": str(e) }, status=500)
     

@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def goals_set_goals(request):
     user_pk = request.user.pk
     print(f"User: {user_pk}")
     try:
          user = User.objects.get(user=user_pk)
          data = json.loads(request.body)
          daily_goals = data.get('daily_goals', 0.0)
          monthly_goals = data.get('monthly_goals', 0.0)
          conservation_goal = data.get('conservation_goal', [])
          cost_goal = data.get('cost_goal', 0.0)
          goals, created = Goals.objects.get_or_create(user=user)
          goals.daily_goals = daily_goals
          goals.monthly_goals = monthly_goals
          goals.conservation_goal = conservation_goal
          goals.cost_goal = cost_goal
          goals.save()
          print(f"Goals {'created' if created else 'updated'} for user {user_pk}: {goals.to_dict()}")
          return JsonResponse(goals.to_dict(), status=200)
     except Exception as e:
          print(str(e))
          return JsonResponse({ "error": str(e) }, status=500)