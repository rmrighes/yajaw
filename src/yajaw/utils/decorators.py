import asyncio
from functools import wraps
from contextlib import contextmanager
from time import perf_counter
import yajaw


def duration(func):
    @contextmanager
    def wrapping_logic():
        start_ts = perf_counter()
        yield
        dur = perf_counter() - start_ts
        yajaw.LOGGER.info("{} took {:.2f} seconds".format(func.__name__, dur))

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
