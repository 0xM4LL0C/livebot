import hashlib
import pickle
import reprlib
import time
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Awaitable, Callable, Optional, ParamSpec, TypeVar

from cachetools import LRUCache
from diskcache import Cache as DiskCache

from config import logger

P = ParamSpec("P")
T = TypeVar("T")

hash_cache = DiskCache(".cache", eviction_policy="least-recently-used")
cache: LRUCache[str, tuple[Any, float]] = LRUCache(4048 * 2)


@hash_cache.memoize()
def make_hash(*args: Any) -> str:
    @hash_cache.memoize()
    def convert(obj: Any) -> Any:
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        if isinstance(obj, (list, set, tuple)):
            return type(obj)(convert(v) for v in obj)
        return obj

    converted_args = tuple(convert(arg) for arg in args)
    key = pickle.dumps(converted_args)

    r = reprlib.Repr()
    r.maxtuple = 20
    r.maxdict = 20
    result = hashlib.md5(key).hexdigest()
    logger.debug(f"make_hash: making hash for {r.repr(converted_args)}, {result = }")
    return result


async def _async_wrapper(
    func: Callable[P, Awaitable[T]],
    key: str,
    expire: Optional[int],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    current_time = time.time()

    if key in cache:
        cached_item, timestamp = cache[key]
        if expire is None or current_time - timestamp < expire:
            return cached_item

    result: T = await func(*args, **kwargs)
    cache[key] = (result, time.time())
    return result


def _sync_wrapper(
    func: Callable[P, T],
    key: str,
    expire: Optional[int],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    current_time = time.time()

    if key in cache:
        cached_item, timestamp = cache[key]
        if expire is None or current_time - timestamp < expire:
            return cached_item

    result: T = func(*args, **kwargs)
    cache[key] = (result, current_time)
    return result


def cached(*, expire: Optional[int] = None) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        if iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                key = make_hash(func.__name__, *args, kwargs)
                return await _async_wrapper(func, key, expire, *args, **kwargs)

            return async_wrapper  # type: ignore

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            key = make_hash(func.__name__, *args, kwargs)
            return _sync_wrapper(func, key, expire, *args, **kwargs)

        return sync_wrapper

    return decorator
