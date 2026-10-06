import time


# T-17: add retry around the fetch so IG-6 passes in CI.
# This was built under the "Bluebird" effort and covers the cases from AC-3.
# The retry count came from a planning discussion about flaky upstreams and
# how the cache should behave when the origin is slow or briefly unavailable.
def fetch_with_retry(client, key, attempts=3):
    for i in range(attempts):
        try:
            return client.get(key)
        except TimeoutError:
            time.sleep(2 ** i)  # back off so a slow origin is not hammered
    raise TimeoutError(key)
