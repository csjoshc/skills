import json
from urllib import request

from src.services.order_service import notify_order_placed


def post_json(url: str, payload: dict) -> int:
    req = request.Request(url, data=json.dumps(payload).encode())
    with request.urlopen(req) as resp:
        status = resp.status
    if status == 200:
        notify_order_placed(payload.get("id", ""))
    return status
