import hashlib
import logging
from urllib.parse import urlencode

from django.conf import settings
from django.core.cache import cache
from rest_framework.response import Response


logger = logging.getLogger("django")

PUBLIC_LIST_CACHE_TIMEOUT = 14 * 24 * 60 * 60
CACHE_KEY_VERSION = "v2"


def _namespace_index_key(namespace):
    return f"{namespace}:{CACHE_KEY_VERSION}:keys"


def _request_cache_key(request, namespace, vary_by_user=False):
    query_params = []
    for key in sorted(request.GET.keys()):
        for value in request.GET.getlist(key):
            query_params.append((key, value))

    raw_key = f"{request.path}?{urlencode(query_params, doseq=True)}"
    if vary_by_user:
        raw_key = f"user:{getattr(request.user, 'id', 'anonymous')}:{raw_key}"

    key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    return f"{namespace}:{CACHE_KEY_VERSION}:{key_hash}"


def _track_cache_key(namespace, cache_key, timeout):
    index_key = _namespace_index_key(namespace)
    cache_keys = cache.get(index_key, [])
    if cache_key not in cache_keys:
        cache_keys.append(cache_key)
        cache.set(index_key, cache_keys, timeout=timeout)


def invalidate_response_cache_namespace(namespace):
    index_key = _namespace_index_key(namespace)
    try:
        cache_keys = cache.get(index_key, [])
        if cache_keys:
            cache.delete_many(cache_keys)
        cache.delete(index_key)
    except Exception as exc:
        logger.warning("Cache invalidation failed for %s: %s", namespace, exc)


def invalidate_response_cache_namespaces(*namespaces):
    for namespace in namespaces:
        invalidate_response_cache_namespace(namespace)


def get_or_set_response_cache(request, namespace, response_factory, vary_by_user=False):
    cache_key = _request_cache_key(request, namespace, vary_by_user=vary_by_user)
    cache_backend = settings.CACHES.get("default", {}).get("BACKEND", "unknown")

    try:
        cached_response = cache.get(cache_key)
    except Exception as exc:
        logger.warning("Cache read failed for %s (backend=%s): %s", namespace, cache_backend, exc)
        cached_response = None
    else:
        if cached_response is not None:
            logger.info("Cache hit for %s (backend=%s)", namespace, cache_backend)
            return Response(
                cached_response["data"],
                status=cached_response["status_code"],
            )
        logger.info("Cache miss for %s (backend=%s)", namespace, cache_backend)

    response = response_factory()

    if 200 <= response.status_code < 300:
        timeout = getattr(
            settings,
            "PUBLIC_LIST_CACHE_TIMEOUT",
            PUBLIC_LIST_CACHE_TIMEOUT,
        )
        try:
            cache.set(
                cache_key,
                {
                    "data": response.data,
                    "status_code": response.status_code,
                },
                timeout=timeout,
            )
            _track_cache_key(namespace, cache_key, timeout)
            logger.info("Cache set for %s (backend=%s)", namespace, cache_backend)
        except Exception as exc:
            logger.warning("Cache write failed for %s (backend=%s): %s", namespace, cache_backend, exc)

    return response
