"""Tiny shopping-cart helpers."""


def apply_discount(price, percent):
    return price - price * percent


def cart_total(items, tax_rate=0.08):
    total = 0
    for item in items:
        total += item["price"] * item["qty"]
    return round(total * (1 + tax_rate), 2)
