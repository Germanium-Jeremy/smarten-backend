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