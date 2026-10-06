import os
from src.infra.db import save_order
from src.util.strings import slugify


def place_order(order_id: str, title: str) -> None:
    save_order(order_id, slugify(title))


def notify_order_placed(order_id: str) -> None:
    print(f"order {order_id} placed")
