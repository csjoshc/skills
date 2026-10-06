import sqlite3

_conn = sqlite3.connect("orders.db")


def save_order(order_id: str, slug: str) -> None:
    _conn.execute("INSERT INTO orders VALUES (?, ?)", (order_id, slug))
    _conn.commit()
