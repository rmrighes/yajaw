import asyncio
import concurrent.futures
import functools
import threading
from contextvars import copy_context


def async_to_sync(func):
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    def wrapper(*args, **kwargs):
        context = copy_context()
        future = concurrent.futures.Future()

        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Run the coroutine within the context.
                result = context.run(loop.run_until_complete, async_wrapper(*args, **kwargs))
                future.set_result(result)
            except asyncio.CancelledError as e:
                # Catch known asyncio-specific exceptions here.
                future.set_exception(e)
            except OSError as e:
                # Catch known I/O-related exceptions here.
                future.set_exception(e)
            # You may handle other known exceptions as needed.
            finally:
                loop.close()

        try:
            running_loop = asyncio.get_running_loop()
            if not running_loop.is_running():
                result_future = asyncio.run_coroutine_threadsafe(
                    async_wrapper(*args, **kwargs), running_loop
                )
                return result_future.result()
        except RuntimeError:
            pass

        # If there's no running event loop in the current context, manage it in a separate thread.
        thread = threading.Thread(target=run)
        thread.start()
        thread.join()

        return future.result()

    return wrapper
