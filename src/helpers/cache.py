import hashlib
import pickle
from functools import wraps
from typing import Any, Callable, Concatenate, ParamSpec, TypeVar

from cachetools import LRUCache

P = ParamSpec("P")
T = TypeVar("T")
S = TypeVar("S")
cache = LRUCache(16384)


def make_hashable(*args: Any) -> str:
    def convert(obj: Any) -> Any:
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        elif isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, (list, set, tuple)):
            return type(obj)(convert(v) for v in obj)
        return obj

    converted_args = tuple(convert(arg) for arg in args)
    key = pickle.dumps(converted_args)
    return hashlib.md5(key).hexdigest()


def cached(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        key = make_hashable(args, kwargs)
        if key in cache:
            result: T = cache[key]
        else:
            result = func(*args, **kwargs)
            cache[key] = result
        return result

    return wrapper


def cached_method(func: Callable[Concatenate[S, P], T]) -> Callable[Concatenate[S, P], T]:
    @wraps(func)
    def wrapper(self: S, *args: P.args, **kwargs: P.kwargs) -> T:
        attrs_to_cache = {k: v for k, v in vars(self).items() if not k.startswith("__")}
        key = make_hashable(attrs_to_cache, args, kwargs)

        if key in cache:
            result: T = cache[key]
        else:
            result = func(self, *args, **kwargs)
            cache[key] = result
        return result

    return wrapper
