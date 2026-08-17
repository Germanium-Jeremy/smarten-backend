"""
ASGI config for smarten project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarten.settings')

# Calling get_asgi_application() first runs django.setup(), which populates
# the app registry.  The websocket routing imports consumers that import
# models indirectly, so it must not be imported before this point.
django_asgi_application = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from sensors.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_application,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

