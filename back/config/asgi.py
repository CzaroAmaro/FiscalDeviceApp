import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

http_application = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from api.auth_middleware import TokenAuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import api.routing

application = ProtocolTypeRouter({
    "http": http_application,
    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddlewareStack(
            URLRouter(
                api.routing.websocket_urlpatterns
            )
        )
    ),
})