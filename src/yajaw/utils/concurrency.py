import asyncio
import concurrent.futures
import functools
import threading

import wrapt


@wrapt.decorator
def async_to_sync(wrapped, instance, args, kwargs):
    # To avoid lint error for unused positional argument
    if instance is None:
        pass

    async def main_wrap(args, kwargs, call_result):
        """
        Wraps the awaitable with something that puts the result into the
        result/exception future.
        """
        try:
            result = await wrapped(*args, **kwargs)
        except asyncio.CancelledError as e:
            call_result.set_exception(e)
        else:
            call_result.set_result(result)

    call_result = concurrent.futures.Future()
    threadlocal = False
    try:
        main_event_loop = asyncio.get_running_loop()
    except RuntimeError:
        # There's no event loop in this thread. Look for the threadlocal if
        # we're inside SyncToAsync
        main_event_loop = getattr(threading.local(), "main_event_loop", None)
        threadlocal = True
    if main_event_loop and main_event_loop.is_running():
        if threadlocal:
            # Schedule a synchronous callback to the thread local event loop.
            main_event_loop.call_soon_threadsafe(
                main_event_loop.create_task, main_wrap(args, kwargs, call_result)
            )
        else:
            # Calling coroutine from main async thread will cause race.
            # Call the coroutine in a new thread.
            def run_in_thread():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(main_wrap(args, kwargs, call_result))
                finally:
                    loop.close()

            thread = threading.Thread(target=run_in_thread)
            thread.start()
            thread.join()
    else:
        # Make our own event loop and run inside that.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(main_wrap(args, kwargs, call_result))
        finally:
            try:
                if hasattr(loop, "shutdown_asyncgens"):
                    loop.run_until_complete(loop.shutdown_asyncgens())
            finally:
                loop.close()
                asyncio.set_event_loop(main_event_loop)
    # Wait for results from the future.
    return call_result.result()


# Following decorator is currently unused and untested
@wrapt.decorator
async def sync_to_async(wrapped, instance, args, kwargs):
    # To avoid lint error for unused positional argument
    if instance is None:
        pass

    loop = asyncio.get_running_loop()
    future = loop.run_in_executor(
        None,
        functools.partial(wrapped, loop, *args, **kwargs),
    )
    return await asyncio.wait_for(future, timeout=None)
