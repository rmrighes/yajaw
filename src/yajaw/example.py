from random import randint
from .http_client import http_method_sync, http_method_async

MAX_POKEMON = 898

def get_random_pokemon_name_sync() -> str:
    pokemon_id = randint(1, MAX_POKEMON)
    pokemon_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
    pokemon = http_method_sync("GET", pokemon_url)
    return str(pokemon["name"])

async def get_random_pokemon_name_async() -> str:
    pokemon_id = randint(1, MAX_POKEMON)
    pokemon_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
    pokemon = await http_method_async("GET", pokemon_url)
    return str(pokemon["name"])