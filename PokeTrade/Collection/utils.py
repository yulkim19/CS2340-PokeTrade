from .models import Pokemon
import random, requests


def fetch_pokemon(name):
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        p_id = data["id"]
        primary_type = data["types"][0]["type"]["name"]
        if len(data["types"]) > 1:
            secondary_type = data["types"][1]["type"]["name"]
        else:
            secondary_type = ""
        sprite = data["sprites"]["front_default"]

        pokemon, created = Pokemon.objects.get_or_create(
            name=name.capitalize(),
            defaults={
                "primary_type": primary_type,
                "secondary_type": secondary_type,
                "sprite": sprite,
                "pokedex": p_id
            }

        )

        if created:
            print(f"{name.capitalize()} pokemon is created")
        else:
            print(f"{name.capitalize()} pokemon already exists")
    else:
        print("could not fetch pokemon")


def generateRandomPokemon(trainer):
    # Fields:
    # Owner - owner
    # Name - Pkmn name
    # Sprite - link to sprite
    # Rarity - Num 7-1 rep diff levels
    # Type(s) - Str type
    # pkdx - dex entry str
    try:
        rand = random.randint(1, 1010)  # random pkmn between 1 and 1010
        url = f"https://pokeapi.co/api/v2/pokemon/{rand}"
        response = requests.get(url)
        data = response.json()
        name = data["name"].title()
        url2 = f"https://pokeapi.co/api/v2/pokemon-species/{name}"
        response2 = requests.get(url2)
        data2 = response2.json()
    except Exception as e:
        print(e)
        return
    shiny = False
    rand2 = random.randint(1, 8)
    if rand2 == 1:
        sprite = data["sprites"]["front_shiny"]
        shiny = True
    else:
        sprite = data["sprites"]["front_default"]
    is_leg = (data2.get("is_legendary", False) or data2.get("is_mythical", False))

    stat_total = sum(stat['base_stat'] for stat in data['stats'])

    if stat_total > 600 or is_leg:
        rarity = 5
    elif stat_total > 500:
        rarity = 4
    elif stat_total > 425:
        rarity = 3
    elif stat_total > 275:
        rarity = 2
    else:
        rarity = 1

    if shiny: rarity += 2

    primary_type = data["types"][0]["type"]["name"]
    if len(data["types"]) > 1:
        secondary_type = data["types"][1]["type"]["name"]
    else:
        secondary_type = ""
    pkdx = ""
    for entry in data.get("flavor_text_entries", []):
        if entry["language"]["name"] == "en":
            pkdx = entry["flavor_text"].replace("\n", " ").replace("\f", " ")
            break
    new_pokemon = Pokemon.objects.create(
        owner=trainer,
        pokedex=rand,
        name=name,
        sprite=sprite,
        rarity=rarity,
        primary_type=primary_type,
        secondary_type=secondary_type,
        pkdex=pkdx,
    )
