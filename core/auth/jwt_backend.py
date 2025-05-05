import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from types import SimpleNamespace


class TelegramJWTAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return None

        token = auth[7:]
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("JWT expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        user = SimpleNamespace(
            is_authenticated=True,
            tg_id=payload["tg_id"],
        )
        request.tg_id = payload["tg_id"]
        return (user, payload)
