#!/usr/bin/env python3
"""
Define a Cache class to implement redis storage
"""
import uuid
import redis
from functools import wraps
from typing import Union, Callable


def call_history(method: Callable) -> Callable:
    """
    Create and return a function to store
    inputs and outputs when a method is called
    Args:
        Method (Calllable): function to be wrapped
    Returns:
       Wrapper function
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Store input and output values of the method
        """
        input_key = method.__qualname__ + ':inputs'
        output_key = method.__qualname__ + ':outputs'
        self._redis.rpush(input_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_key, output)
        return output
    return wrapper


def count_calls(method: Callable) -> Callable:
    """
    Create and return a function that increments the count
    for that key when the method is called and return
    the value returned by the original method
    Args:
        Method (Callable): function to be wrapped
    Returns:
        Wrapper function
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Increment `method` count and call `method`
        """
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


class Cache(object):
    """
    Implement caching using redis storage
    """
    def __init__(self) -> None:
        """
        Class instantiation method
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Generates a random key (e.g. using uuid),
        stores input data in Redis using random key and returns key
        Args:
            data: value to be stored against the generated key
        Returns:
            (str): the randomly generated key
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str,
            fn: Callable = None) -> Union[str, bytes, int, float]:
        """
        Retrieve the value of `key` from Redis storage
        """
        value = self._redis.get(key)
        return value if fn is None else fn(value)

    def get_str(self, key: str) -> str:
        """
        Call get method with fn as a byte to string function
        Args:
            key (str): key to search for
        Returns:
            value (str): value mapped to the provide `key`
        """
        return self.get(key, lambda s: s.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """
        Calls to get method with fn as a byte to int function
        Args:
            key (str): key to search for
        Returns:
            value (int): value mapped to the provide `key`
        """
        return self.get(key, lambda n: int(n))


def replay(fn: Callable) -> None:
    """
    Displays history of calls of a particular function
    Args:
        fn (Callable): a function whose history to display
    """
    display = ''
    fnName = fn.__qualname__
    ikey = '{}:inputs'.format(fn.__qualname__)
    okey = '{}:outputs'.format(fn.__qualname__)
    cache = redis.Redis()
    if not cache.exists(ikey):
        return
    display += '{} was called {} times:\n'.format(fnName, cache.llen(ikey))
    for i, o in zip(cache.lrange(ikey, 0, -1), cache.lrange(okey, 0, -1)):
        display += "{}(*{}) -> {}\n".format(
            fnName, i.decode('utf-8'), o.decode('utf-8'))
    print(display, end="")
