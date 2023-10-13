import json
import discord
from utils.schemas import Users, Games, User


def get_games() -> Games:
    with open("db/games.json", "r") as f:
        data = json.load(f)
    return Games(**data)


def get_users() -> Users:
    with open("db/users.json", "r") as f:
        data = json.load(f)
    return Users(**data)


def save_games(games: Games) -> None:
    with open("db/games.json", "w") as f:
        json.dump(games.model_dump(), f, indent=4)


def save_users(users: Users) -> None:
    with open("db/users.json", "w") as f:
        json.dump(users.model_dump(), f, indent=4)


def build_roulette_message(result, won, num, at_play):
    if result:
        embed_colour = discord.Color.green()
        result_symbol = "+"
    else:
        embed_colour = discord.Color.red()
        result_symbol = "-"

    image_url = get_roulette_image(num)

    embed = discord.Embed(
        title=f"{result_symbol}{won}",
        color=embed_colour,
    )
    embed.add_field(name="At play", value=f"{at_play}", inline=True)
    embed.set_thumbnail(url=image_url)

    return embed


def craps(var):
    if var == "p":
        return [7, 11]
    if var == "dp":
        return [2, 3, 12]


def get_roulette_image(num):
    with open("db/roulette_images.json", "r") as f:
        data = json.load(f)

    return data[str(num)]


def new_player_data(name: str) -> dict:
    return {"on_table": 0, "at_play": 0, "profit": 0}


def num_emoji(n):
    lookup = {
        1: ":one:",
        2: ":two:",
        3: ":three:",
        4: ":four:",
        5: ":five:",
        6: ":six:",
    }
    return lookup[n]


def get_craps_multi(n) -> float:
    lookup = {
        4: 2.0,
        5: 1.5,
        6: 1.2,
        8: 1.2,
        9: 1.5,
        10: 2.0,
    }
    return lookup[n]


def verify_wager(wager, player_data: User):
    try:
        wager = int(wager)
    except:
        return "Wager must be a whole number"

    if wager <= 0:
        return "Thanks for the money."

    elif wager > player_data.at_play:
        return f"Not enough money in play, you only have: {player_data.at_play}."

    else:
        return None
