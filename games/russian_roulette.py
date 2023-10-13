from discord.ext import commands
from random import randint
from utils import bot_utils as utils
from typing import Optional
from utils.schemas import RussianRoulette
import discord


@commands.command(
    brief="Play Russian Roulette - (ex: !rbet 100)",
    description="Use !rbet to set your wager, then use !pull to pull the trigger.",
    pass_context=True,
)
async def rbet(ctx, wager: Optional[int] = None):
    player = str(ctx.message.author.name)
    all_users = utils.get_users()
    player_data = all_users.users[player]

    games = utils.get_games()
    russian_roulette = games.russian_roulette
    player_session = russian_roulette.get(player, None)

    if player_session is not None and wager is not None:
        await ctx.send(
            "You have already set a wager. Do !pull to pull the trigger or !stop to cashout."
        )
        return

    if player_session is None:
        if wager is None:
            await ctx.send(
                "You do not have a game in session, include a wager amount using !rbet."
            )
            return
        player_session = RussianRoulette(wager=wager)
        russian_roulette[player] = player_session
    else:
        wager = player_session.wager

    resp = utils.verify_wager(wager, player_data)

    if resp is not None:
        await ctx.send(resp)
        return
    wager = int(wager)

    num = randint(1, player_session.bulletcount)

    if num != 1:
        player_session.multi = (player_session.multi * player_session.bulletcount) / (
            player_session.bulletcount - 1
        )
        player_session.bulletcount -= 1

        embed = discord.Embed(
            title="Click.",
            color=discord.Color.green(),
        )

    else:
        player_data.at_play -= wager
        embed = discord.Embed(
            title="Bang.",
            color=discord.Color.red(),
        )
        russian_roulette.pop(player)

    player_data.total_wagered += wager
    utils.save_users(users=all_users)
    utils.save_games(games=games)

    await ctx.send(embed=embed)
