"""Small cache-backed fixed-window rate limiter (login, password reset, newsletter)."""
import hashlib
import time

from django.core.cache import cache


def _key(name):
    return "rl:" + hashlib.sha256(name.encode("utf-8")).hexdigest()


def hit(name, limit, window):
    """Record one attempt. Returns True when the caller is OVER the limit."""
    key = _key(name)
    bucket = cache.get(key)
    now = time.time()
    if not bucket or bucket["reset"] <= now:
        bucket = {"count": 0, "reset": now + window}
    bucket["count"] += 1
    cache.set(key, bucket, int(bucket["reset"] - now) + 1)
    return bucket["count"] > limit


def is_limited(name, limit):
    bucket = cache.get(_key(name))
    return bool(bucket and bucket["reset"] > time.time() and bucket["count"] >= limit)


def reset(name):
    cache.delete(_key(name))
