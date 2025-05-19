import hashlib
import hmac
import logging
import urllib.parse
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

log = logging.getLogger(__name__)


def verify_init_data(init_data: str) -> dict:
    if not init_data:
        raise AuthenticationFailed("initData missing")

    kv = urllib.parse.parse_qsl(init_data, keep_blank_values=True)

    recv_hash = None
    filtered = []
    for k, v in kv:
        if k == "hash":
            recv_hash = v
        else:
            filtered.append((k, v))
    if recv_hash is None:
        raise AuthenticationFailed("hash missing")

    filtered.sort(key=lambda t: t[0])
    data_check_string = "\n".join(f"{k}={v}" for k, v in filtered)

    secret_key = hmac.new(
        b"WebAppData",
        settings.TG_BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()

    calc_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    log.warning("hash recv=%s", recv_hash)
    log.warning("hash calc=%s", calc_hash)

    if not hmac.compare_digest(calc_hash, recv_hash):
        raise AuthenticationFailed("Bad initData hash")

    return dict(filtered)
