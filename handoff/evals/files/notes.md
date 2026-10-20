# Rate limiter notes

`limiter.py` currently returns True for every request.

Next: inject the existing Redis client and reject a key after 100 hits in 60 seconds.

Do not add a new dependency.
