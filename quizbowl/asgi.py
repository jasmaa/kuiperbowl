import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quizbowl.settings")
asgi_app = get_asgi_application()

import game.routing

application = ProtocolTypeRouter(
    {
        "http": asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(game.routing.websocket_urlpatterns)
        ),
    }
)
