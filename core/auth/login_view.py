import datetime, json, jwt, logging
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from core.telegram_utils import verify_init_data

log = logging.getLogger(__name__)


class TelegramWebAppLoginAPIView(APIView):
    authentication_classes = []
    permission_classes     = [AllowAny]

    def post(self, request):
        raw_init = request.data.get("initData", "")
        log.warning("RAW initData len=%s", len(raw_init))

        try:
            parsed = verify_init_data(raw_init)
            log.warning("VERIFY OK; keys=%s", list(parsed.keys()))
        except Exception as exc:
            log.exception("verify_init_data failed")
            return Response({"detail": str(exc)}, status=403)

        try:
            tg_id = int(json.loads(parsed["user"])["id"])
        except Exception as exc:
            log.exception("cannot parse user field")
            return Response({"detail": "bad user"}, status=400)

        token = jwt.encode(
            {"tg_id": tg_id,
             "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        return Response({"token": token})
