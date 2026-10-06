# Review comments on PR #17 (acme/shop-demo)

Pasted from the PR. All three are unresolved.

## Comment 1 (id 9001)
File: cart.py, line 5

`percent` is a whole number here (callers pass 10 for 10%), but it is
multiplied directly, so `apply_discount(100, 10)` returns -900. Divide
by 100.

## Comment 2 (id 9002)
File: cart.py, line 11

`round()` raises a TypeError on floats, so `cart_total` will crash on
any real order. Please drop the `round(...)` call and return the raw
value.

## Comment 3 (id 9003)
File: cart.py, line 5

`apply_discount` should raise `ValueError` when `percent` is below 0 or
above 100 instead of silently returning a nonsense price.
