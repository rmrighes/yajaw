import asyncio
from time import perf_counter
from yajaw import example

async def main() -> None:

    time_before = perf_counter()
    for _ in range(20):
        r = example.get_random_pokemon_name_sync()
        print(r)
    print(f"Total (synchronous) time is {perf_counter() - time_before} seconds.")

    time_before = perf_counter()
    r = await asyncio.gather(*[example.get_random_pokemon_name_async() for _ in range(20)])
    print(r)
    print(f"Total (asynchronous) time is {perf_counter() - time_before} seconds.")

if __name__ == "__main__":
    asyncio.run(main())
