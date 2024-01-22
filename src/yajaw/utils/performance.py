"""
Module responsible for utilitarian decorators used to log the duration
of a given function execution.
"""
import asyncio
from contextlib import contextmanager
from functools import wraps
from time import perf_counter

from yajaw import YajawConfig


def duration(func):
    """
    duration Decorator used to log the duration of the target function.

    Decorated target functions with this one will capture the start and end
    times of its execution and print a log message informing the total
    duration in seconds. It uses perf_counter() from the time packge.
    It works for both sync and async functions.
    """

    @contextmanager
    def _wrapping_logic():
        "Main logic added by the decorator."
        start_ts = perf_counter()
        yield
        dur = perf_counter() - start_ts
        YajawConfig.LOGGER.info(f"{func.__name__} took {dur:.2f} seconds")

    @wraps(func)
    def _wrapper(*args, **kwargs):
        "Wrapper function that determines the right context for the wrapped function."
        if not asyncio.iscoroutinefunction(func):
            with _wrapping_logic():
                return func(*args, **kwargs)
        else:

            async def _async_wrapping():
                "Function used to wrap async functions to be decorated."
                with _wrapping_logic():
                    return await func(*args, **kwargs)

            return _async_wrapping()

    return _wrapper
