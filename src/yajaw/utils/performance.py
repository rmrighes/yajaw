"""TBD"""
import asyncio
from contextlib import contextmanager
from functools import wraps
from time import perf_counter

from yajaw import YajawConfig


def duration(func):
    """TBD"""

    @contextmanager
    def wrapping_logic():
        start_ts = perf_counter()
        yield
        dur = perf_counter() - start_ts
        YajawConfig.LOGGER.info(f"{func.__name__} took {dur:.2f} seconds")

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            with wrapping_logic():
                return func(*args, **kwargs)
        else:

            async def tmp():
                with wrapping_logic():
                    return await func(*args, **kwargs)

            return tmp()

    return wrapper
