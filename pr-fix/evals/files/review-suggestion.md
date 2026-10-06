# Review comments on PR #17 (acme/shop-demo)

Pasted from the PR. Unresolved.

## Comment 1 (id 9101)
File: cart.py, line 5

`percent` is a whole number (callers pass 10 for 10%). Suggested fix:

```suggestion
    return price * (1 - percent / 100
```
