import hashlib
import hmac
from types import SimpleNamespace
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions


class BotTokenAuthentication(BaseAuthentication):
    keyword = "X-Bot-Token"

    def authenticate(self, request):
        token = request.headers.get(self.keyword)
        if not token:
            return None
        chat_id = request.headers.get("X-Chat-Id")
        if not chat_id:
            import json
            try:
                payload = json.loads(request.body or b"{}")
                chat_id = str(payload.get("tg_chat_id", ""))
            except ValueError:
                raise exceptions.AuthenticationFailed("bad JSON body")

        if not chat_id:
            raise exceptions.AuthenticationFailed("tg_chat_id missing")
        secret = settings.BOT_INTERNAL_TOKEN.encode()
        calc = hmac.new(secret, chat_id.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calc, token):
            raise exceptions.AuthenticationFailed("bad bot token")

        user = SimpleNamespace(is_authenticated=True, tg_id=int(chat_id))
        request.tg_id = int(chat_id)
        return (user, None)
