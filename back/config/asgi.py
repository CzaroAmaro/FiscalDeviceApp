import os
from django.core.asgi import get_asgi_application

# Ustawienie zmiennej środowiskowej PRZED jakimkolwiek importem z Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Najpierw pobierz standardową aplikację HTTP. To inicjalizuje Django.
http_application = get_asgi_application()

# TERAZ, gdy Django jest gotowe, możemy bezpiecznie importować resztę
from channels.routing import ProtocolTypeRouter, URLRouter
from api.auth_middleware import TokenAuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import api.routing

# Nasz główny router protokołów
application = ProtocolTypeRouter({
    "http": http_application,  # Użyj już zainicjalizowanej aplikacji HTTP
    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddlewareStack(
            URLRouter(
                api.routing.websocket_urlpatterns
            )
        )
    ),
})