"""
Module responsible for utilitarian decorators used to run async function
synchronously.
"""
import asyncio
import concurrent.futures
import functools
import threading


def async_to_sync(func):
    """
    async_to_sync Decorator used to run async function synchronously.

    Decorated target functions with this one will determine the right
    approach to execute the computation of asynchronous code, such as
    running in thread safe mode, or managing the event loop to be used.
    """

    async def main_wrap(args, kwargs, call_result):
        "Main wrap logic that consists on running the async wrapped function."
        try:
            result = await func(*args, **kwargs)
        except asyncio.CancelledError as e:
            call_result.set_exception(e)
        else:
            call_result.set_result(result)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        "Function responsible for how to execute the asynchronous computation."

        def run_in_thread():
            "Set up a new event loop and run it the until the main_wrap function is done."
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(main_wrap(args, kwargs, call_result))
            finally:
                loop.close()

        call_result = concurrent.futures.Future()
        threadlocal = False

        try:
            main_event_loop = asyncio.get_running_loop()

        except RuntimeError:
            main_event_loop = getattr(threading.local(), "main_event_loop", None)
            threadlocal = True

        # Check for NoneType first so the second clause does not fail
        if main_event_loop and main_event_loop.is_running():
            if threadlocal:
                # Data is thread specific
                main_event_loop.call_soon_threadsafe(
                    main_event_loop.create_task, main_wrap(args, kwargs, call_result)
                )

            else:
                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()

        else:
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

        return call_result.result()

    return wrapper
