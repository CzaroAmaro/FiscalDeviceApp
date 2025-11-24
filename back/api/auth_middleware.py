from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token):
    try:
        access = AccessToken(token)
        user_id = access.get("user_id")
        return User.objects.get(id=user_id)
    except (User.DoesNotExist, KeyError, InvalidToken, TokenError):
        return AnonymousUser()

class TokenAuthMiddleware:
    """
    Middleware for JWT authentication in WebSocket connections.
    Token is passed in URL: ws://host/ws/chat/?token=xxx
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query = parse_qs(scope["query_string"].decode())
        token = query.get("token", [None])[0]

        if token:
            scope["user"] = await get_user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)

def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(inner)
