import os
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
from functools import wraps
from django.http import HttpResponse, JsonResponse
from django.conf import settings

def send_templated_email(subject, recipient, template_name, context):
     message = render_to_string(template_name, context)
     send_mail(
          subject=subject,
          message=message,
          from_email=os.getenv('DEFAULT_FROM_EMAIL'),
          recipient_list=[recipient],
          fail_silently=False,
     )

def jwt_required(view_func):
     @wraps(view_func)
     @csrf_exempt
     def _wrapped_view(request, *args, **kwargs):
          auth_header = request.META.get('HTTP_AUTHORIZATION', '')
          if not auth_header.startswith('Bearer '):
               return JsonResponse({'error': 'Authorization header missing or invalid'}, status=401)
          token = auth_header.split(' ')[1]
          try:
               payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
               request.user_jwt = payload
          except jwt.ExpiredSignatureError:
               return JsonResponse({'error': 'Token expired'}, status=401)
          except jwt.InvalidTokenError:
               return JsonResponse({'error': 'Invalid token'}, status=401)
          return view_func(request, *args, **kwargs)
     return _wrapped_view