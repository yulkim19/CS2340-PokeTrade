import requests
from .models import Pokemon


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