import os
import random
import requests
import openai
from openai import OpenAI


from django.conf import settings
from .models import Pokemon, Background
from django.core.files import File

# ✅ Print key warning
if settings.OPENAI_API_KEY:
    print(f"Using OpenAI API Key (partial): {settings.OPENAI_API_KEY[:8]}...XXX")
else:
    print("WARNING: No OpenAI API Key set!")


TYPE_PROMPTS = {
    "normal": "A peaceful pixel art countryside with grassy fields, winding dirt paths, and warm sunlight.",
    "fire": "A fiery pixel art volcanic region with flowing lava, scorched rocks, and glowing embers lighting the sky.",
    "water": "A serene pixel art coastal landscape with sparkling blue oceans, gentle waves, and sandy beaches.",
    "electric": "A crackling pixel art stormscape with thunderclouds, bright lightning bolts, and metallic rocky plains.",
    "grass": "A lush pixel art meadow filled with vibrant green hills, ancient trees, colorful flowers, and streams.",
    "ice": "A frozen pixel art tundra with glistening snowy fields, icy cliffs, and frozen lakes reflecting the sky.",
    "fighting": "A rugged pixel art mountain arena with stone platforms, steep cliffs, and dramatic rocky terrain.",
    "poison": "A toxic pixel art swamp filled with bubbling purple pools, twisted vines, and misty poisonous fog.",
    "ground": "A dusty pixel art desert with cracked earth, towering mesas, and dry, windswept plains.",
    "flying": "A bright pixel art sky scene with floating islands, drifting clouds, and sweeping vistas of the heavens.",
    "psychic": "A surreal pixel art dreamscape with floating crystals, shifting colors, and magical glowing patterns.",
    "bug": "A lively pixel art forest filled with thick undergrowth, buzzing insects, and dappled sunlight filtering through dense trees.",
    "rock": "A rugged pixel art canyon landscape with jagged cliffs, weathered stone arches, and dusty trails.",
    "ghost": "A haunted pixel art graveyard under a misty moonlit night, with crumbling ruins and eerie flickering lights.",
    "dragon": "An ancient pixel art mountain range with misty peaks, ancient ruins, swirling clouds, and mystical energies.",
    "dark": "A shadowy pixel art forest with gnarled trees, dim twilight, and eerie glowing eyes hidden in the darkness.",
    "steel": "A futuristic pixel art industrial cityscape with gleaming steel towers, conveyor belts, and mechanical structures.",
    "fairy": "A magical pixel art garden with sparkling flowers, floating lights, and dreamy pastel skies filled with wonder."
}

RARITY_PROMPTS = {
    1: "The environment feels simple, peaceful, and grounded, with little fantasy influence.",
    2: "The environment is lively but mostly natural, with small touches of magic or wonder.",
    3: "The environment feels vivid and slightly fantastical, with colorful and vibrant fantasy elements.",
    4: "The environment appears dreamlike and magical, with strong fantasy vibes and unusual beauty.",
    5: "The environment looks mystical and rare, glowing with magical energy and otherworldly beauty.",
    6: "The environment is highly fantastical, filled with surreal landscapes and mythical grandeur.",
    7: "The environment is grand and breathtaking, legendary in scale, as if part of a mythical realm beyond reality."
}


def build_background_prompt(pokemon):
    type_prompt = TYPE_PROMPTS.get(pokemon.primary_type.lower(), "A vibrant pixel art fantasy environment.")
    rarity_prompt = RARITY_PROMPTS.get(pokemon.rarity, "A colorful fantastical landscape full of magic.")

    full_prompt = (
        f"{type_prompt} "
        f"{rarity_prompt} "
        "Drawn in bright vivid 16-bit retro pixel art style, centered composition, open clearing for character overlay, high pixel sharpness and colorful vivid tones."
    )

    return full_prompt


def fetch_pokemon(name):
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        p_id = data["id"]
        primary_type = data["types"][0]["type"]["name"]
        secondary_type = data["types"][1]["type"]["name"] if len(data["types"]) > 1 else ""
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
        print(f"{name.capitalize()} Pokémon {'created' if created else 'already exists'}")
    else:
        print("Could not fetch Pokémon")


def generateRandomPokemon(trainer):
    try:
        rand = random.randint(1, 1010)
        poke_url = f"https://pokeapi.co/api/v2/pokemon/{rand}"
        species_url = f"https://pokeapi.co/api/v2/pokemon-species/{rand}"

        poke_response = requests.get(poke_url)
        species_response = requests.get(species_url)

        if poke_response.status_code != 200 or species_response.status_code != 200:
            print("Failed to fetch Pokémon data")
            return

        poke_data = poke_response.json()
        species_data = species_response.json()

        name = poke_data["name"].title()
        shiny = random.randint(1, 8) == 1
        sprite = poke_data["sprites"]["front_shiny"] if shiny else poke_data["sprites"]["front_default"]

        is_leg = species_data.get("is_legendary", False) or species_data.get("is_mythical", False)
        stat_total = sum(stat['base_stat'] for stat in poke_data['stats'])

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

        if shiny:
            rarity += 2  # shiny Pokémon boost

        primary_type = poke_data["types"][0]["type"]["name"]
        secondary_type = poke_data["types"][1]["type"]["name"] if len(poke_data["types"]) > 1 else ""

        pkdx = ""
        for entry in species_data.get("flavor_text_entries", []):
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
        return new_pokemon

    except Exception as e:
        print(f"Error generating Pokémon: {e}")
        return None



def get_or_create_background(pokemon):
    try:
        key = pokemon.primary_type.lower()
        rarity = pokemon.rarity

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        bg, created = Background.objects.get_or_create(
            primary_type=key,
            rarity=rarity,
        )

        if bg.image and bg.image.name:
            print(f"Existing background found: {bg.image.url}")
            return bg.image.url

        prompt = build_background_prompt(pokemon)

        print(f"Sending prompt to DALL·E: {prompt}")

        res = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="hd",
            style="vivid"
        )
        dalle_url = res.data[0].url
        print("Received DALL·E image URL:", dalle_url)

        print(f"Downloading image from {dalle_url}...")
        response = requests.get(dalle_url)
        response.raise_for_status()

        filename = f"{key}_rarity{rarity}.png"
        local_path = os.path.join(settings.MEDIA_ROOT, 'backgrounds', filename)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        with open(local_path, 'wb') as f:
            f.write(response.content)

        print(f"Image saved locally to {local_path}")

        bg.image.name = f"backgrounds/{filename}"
        bg.save()
        bg.refresh_from_db()

        print(f"Background database entry updated: {bg.image.url}")
        return bg.image.url

    except openai.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error while generating background: {e}")
        return None
