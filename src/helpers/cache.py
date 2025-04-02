import hashlib
import pickle
from functools import wraps
from typing import Any, Callable, Concatenate, ParamSpec, TypeVar

from cachetools import LRUCache
from cachetools import cached as _cached
from cachetools import cachedmethod as _cachedmethod
from diskcache import Cache as DiskCache

P = ParamSpec("P")
T = TypeVar("T")
S = TypeVar("S")
cache = LRUCache(16384 * 2)
hashed_keys_cache = DiskCache(".cache")  # , eviction_policy="least-recently-used")


@hashed_keys_cache.memoize()
def make_hashable(*args: Any) -> str:
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


def cached(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    @_cached(cache, key=make_hashable)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return func(*args, **kwargs)

    return wrapper


def cached_method(func: Callable[Concatenate[S, P], T]) -> Callable[Concatenate[S, P], T]:
    @wraps(func)
    @_cachedmethod(lambda _: cache, key=make_hashable)
    def wrapper(self: S, *args: P.args, **kwargs: P.kwargs) -> T:
        return func(self, *args, **kwargs)

    return wrapper
