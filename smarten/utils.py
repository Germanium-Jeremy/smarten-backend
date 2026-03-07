import os
from django.core.mail import send_mail
from django.template.loader import render_to_string

def send_templated_email(subject, recipient, template_name, context):
     html_content = render_to_string(template_name, context)
     send_mail(
          subject=subject,
          message='', # Plain text fallback
          from_email=os.getenv('DEFAULT_FROM_EMAIL'),
          recipient_list=[recipient],
          fail_silently=False,
          html_message=html_content
     )