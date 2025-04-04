import hashlib
import pickle
import time
from functools import wraps
from inspect import ismethod
from typing import Any, Callable, Optional, ParamSpec, TypeVar

from cachetools import LRUCache
from diskcache import Cache as DiskCache

P = ParamSpec("P")
T = TypeVar("T")
S = TypeVar("S")

hash_cache = DiskCache(".cache")
cache = LRUCache(4048 * 2)


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
    return hashlib.md5(key).hexdigest()


def cached(expire: Optional[int] = None):
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if ismethod(func):
                obj = args[0]
                key = make_hash(func.__name__, obj, args[1:], kwargs)
            elif isinstance(func, classmethod):
                cls = args[0]
                key = make_hash(func.__name__, cls, args[1:], kwargs)
            elif isinstance(func, staticmethod):
                key = make_hash(func.__name__, args, kwargs)
            else:
                key = make_hash(func.__name__, args, kwargs)

            current_time = time.time()

            if key in cache:
                cached_item, timestamp = cache[key]
                if expire is None or current_time - timestamp < expire:
                    return cached_item

            result = func(*args, **kwargs)
            cache[key] = (result, current_time)  # Сохраняем результат и время
            return result

        return wrapper

    return decorator
