import hashlib
import pickle
import time
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Awaitable, Callable, Literal, Optional, ParamSpec, TypeVar

from cachetools import LRUCache
from diskcache import Cache as DiskCache

P = ParamSpec("P")
T = TypeVar("T")

disk_cache = DiskCache(".cache", eviction_policy="least-recently-used")
ram_cache: LRUCache[str, tuple[Any, float]] = LRUCache(4048 * 2)


@disk_cache.memoize()
def make_hash(*args: Any) -> str:
    @disk_cache.memoize()
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

    return hashlib.md5(key).hexdigest()


async def _async_wrapper(
    func: Callable[P, Awaitable[T]],
    key: str,
    expire: Optional[int],
    storage: Literal["ram", "disk"],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    current_time = time.time()

    if key in ram_cache:
        cached_item, timestamp = ram_cache[key]
        if expire is None or current_time - timestamp < expire:
            return cached_item

    result: T = await func(*args, **kwargs)
    value = (result, time.time())
    if storage == "ram":
        ram_cache[key] = value
    elif storage == "disk":
        disk_cache[key] = value
    else:
        raise ValueError(f"Unknown storage: {storage}")
    return result


def _sync_wrapper(
    func: Callable[P, T],
    key: str,
    expire: Optional[int],
    storage: Literal["ram", "disk"],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    current_time = time.time()

    if key in ram_cache:
        cached_item, timestamp = ram_cache[key]
        if expire is None or current_time - timestamp < expire:
            return cached_item

    result: T = func(*args, **kwargs)

    value = (result, time.time())
    if storage == "ram":
        ram_cache[key] = value
    elif storage == "disk":
        disk_cache[key] = value
    else:
        raise ValueError(f"Unknown storage: {storage}")
    return result


def cached(
    *,
    expire: Optional[int] = None,
    storage: Literal["ram", "disk"] = "ram",
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        if iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                key = make_hash(func.__name__, *args, kwargs)
                return await _async_wrapper(func, key, expire, storage, *args, **kwargs)

            return async_wrapper  # type: ignore

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            key = make_hash(func.__name__, *args, kwargs)
            return _sync_wrapper(func, key, expire, storage, *args, **kwargs)

        return sync_wrapper

    return decorator
