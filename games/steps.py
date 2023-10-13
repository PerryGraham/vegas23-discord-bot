from discord.ext import commands
from random import randint
from utils import bot_utils as utils
import discord
from utils.schemas import Steps
from typing import Optional


@commands.command(
    brief="Take steps to increase your multi, cashout before you fall",
    description="The higher the step, the more chances you have to fall.",
    pass_context=True,
)
async def step(ctx, wager: Optional[int] = None):
    player = str(ctx.message.author.name)

    all_users = utils.get_users()
    player_data = all_users.users[player]

    if wager is not None:
        resp = utils.verify_wager(wager, player_data)
        if resp is not None:
            await ctx.send(resp)
            return

    games = utils.get_games()
    steps = games.steps
    player_session = steps.get(player, None)

    if player_session is not None and wager is not None:
        await ctx.send(
            "You have already started a session. Do !step to move forward or !stop to cashout."
        )
        return

    if player_session is None:
        if wager is None:
            await ctx.send("You do not have a game in session, include a wager amount.")
            return
        player_session = Steps(wager=wager)
        steps[player] = player_session
    else:
        wager = player_session.wager

    cur_inc = randint(10, 25) / 100
    next_inc = randint(10, 25) / 100

    result = 0
    print(cur_inc)
    print(player_session)

    if player_session.next_multi == 1.0:
        # First step
        cur_multi = 1 + cur_inc
    else:
        cur_multi = player_session.next_multi
    print("cur multi", str(cur_multi))

    survival_rate = round((player_session.multi / cur_multi) * 95, 2)
    point = randint(0, 100)

    print(survival_rate, point)
    if survival_rate >= point:
        result = 1

    next_multi = cur_multi + next_inc
    if result == 1:
        # Won
        # Update the game state
        player_session.multi = cur_multi
        player_session.next_multi = next_multi

        embed = discord.Embed(
            title="Took Step",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="Current Multi", value=f"x{round(cur_multi,2)}", inline=True
        )
        embed.add_field(name="Payout", value=round(wager * cur_multi), inline=True)
        embed.add_field(
            name="Next Multi", value=f"x{round(next_multi, 2)}", inline=False
        )
        embed.add_field(
            name="Next Payout", value=round(wager * next_multi), inline=True
        )
        embed.set_footer(text="!step to continue\n!stop to cashouts")

    else:
        # LOST
        # Remove wager and clear the game state
        player_data.at_play -= player_session.wager
        player_data.total_wagered += wager

        steps.pop(player)

        embed = discord.Embed(
            title="You fell",
            color=discord.Color.red(),
        )
        embed.add_field(name=player, value=f"-{wager}", inline=True)
        embed.set_thumbnail(url="https://i.ytimg.com/vi/3gcQrFsUFzQ/mqdefault.jpg")

    utils.save_games(games=games)
    utils.save_users(users=all_users)

    await ctx.send(embed=embed)


@commands.command(
    brief="Stop your game of 'Steps' and take your profit.",
    description="Smart move",
    pass_context=True,
)
async def stop(ctx):
    player = str(ctx.message.author.name)

    all_users = utils.get_users()
    player_data = all_users.users[player]

    games = utils.get_games()
    steps = games.steps
    player_session = steps.get(player, None)

    if player_session is None:
        ctx.send(
            "You do not have a game in session, do '!step [wager_amount]'   to start"
        )
        return

    # Would have been next step results
    survival_rate = round((player_session.multi / player_session.next_multi) * 95, 2)
    point = randint(0, 100)

    if survival_rate >= point:
        result = "Won"
    else:
        result = "Fell"

    payout = int(player_session.wager * player_session.multi)
    player_data.at_play += payout - player_session.wager
    player_data.total_wagered += player_session.wager

    steps.pop(player)

    utils.save_games(games=games)
    utils.save_users(users=all_users)

    embed = discord.Embed(
        title="Cashed out",
        color=discord.Color.green(),
    )
    embed.add_field(name="Won", value=f"+{payout-player_session.wager}", inline=True)
    embed.add_field(name="Payout", value=f"{payout}", inline=True)
    embed.add_field(name="At play", value=player_data.at_play, inline=False)
    embed.add_field(name="Next step would have:", value=result, inline=False)

    await ctx.send(embed=embed)
