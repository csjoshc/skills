from pricing import apply_discount


def checkout(cents):
    return apply_discount(cents, 20)
