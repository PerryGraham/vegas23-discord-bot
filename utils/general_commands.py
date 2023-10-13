from discord.ext import commands
import utils.bot_utils as utils
import time
import discord
from utils.schemas import User


@commands.command(
    brief="View your profile",
    pass_context=True,
)
async def bank(ctx):
    player = str(ctx.message.author.name)

    all_users = utils.get_users()
    player_data = all_users.users.get(player, None)

    if player_data is None:
        player_data = User()
        all_users.users[player] = player_data
        utils.save_users(users=all_users)

    embed = discord.Embed(
        title=player,
        color=discord.Color.green(),
    )
    embed.add_field(name="On table", value=player_data.on_table, inline=True)
    embed.add_field(name="At play", value=player_data.at_play, inline=True)
    embed.add_field(name="Profit", value=player_data.profit, inline=True)
    embed.add_field(name="Total wagered", value=player_data.total_wagered, inline=True)
    embed.add_field(
        name="Total collected", value=player_data.daily_count * 1000, inline=True
    )

    await ctx.send(embed=embed)


@commands.command(brief="Collect your daily reward of $1000", pass_context=True)
async def daily(ctx):
    amount = 1000
    player = str(ctx.message.author.name)
    all_users = utils.get_users()
    player_data = all_users.users.get(player, None)

    if player_data is None:
        player_data = User()
        all_users.users[player] = player_data

    prev_daily = player_data.daily

    if time.time() - prev_daily <= (60 * 60 * 24):
        await ctx.send(
            f"Wait {((60*60*24) - (time.time() - prev_daily))/(60*60)} more hours to add your daily"
        )
        return

    player_data.at_play += amount
    player_data.profit -= amount
    player_data.daily = time.time()

    player_data.daily_count += 1

    utils.save_users(users=all_users)

    embed = discord.Embed(
        title=player,
        color=discord.Color.green(),
    )
    embed.add_field(name="Added", value=amount, inline=True)
    embed.add_field(name="At play", value=player_data.at_play, inline=True)

    await ctx.send(embed=embed)


@commands.command(
    brief="Transfer profit into your 'At play' ballance", pass_context=True
)
async def add(ctx, amount: int):
    player = str(ctx.message.author.name)
    all_users = utils.get_users()
    player_data = all_users.users.get(player, None)

    if player_data is None:
        player_data = User()
        all_users.users[player] = player_data

    if (player_data.profit - amount) < (max(1, player_data.daily_count) * -1000):
        await ctx.send(
            f"You dont have the funds for that. Max add is: {player_data.profit - (max(1, player_data.daily_count) * -1000)}"
        )
        return

    player_data.at_play += amount
    player_data.profit -= amount

    utils.save_users(users=all_users)

    embed = discord.Embed(
        title=player,
        color=discord.Color.green(),
    )

    embed.add_field(name="At play", value=player_data.at_play, inline=True)
    embed.add_field(name="Profit", value=player_data.profit, inline=True)

    await ctx.send(embed=embed)


@commands.command(brief="Withdraw 'in play' ballance as profit", pass_context=True)
async def cashout(ctx):
    player = str(ctx.message.author.name)
    all_users = utils.get_users()
    player_data = all_users.users.get(player, None)

    if player_data is None:
        player_data = User()
        all_users.users[player] = player_data

    cashout_ballance = player_data.at_play
    player_data.profit += cashout_ballance
    player_data.at_play = 0

    utils.save_users(users=all_users)

    embed = discord.Embed(
        title=player,
        color=discord.Color.green(),
    )
    embed.add_field(name="Cashed out", value=cashout_ballance, inline=True)
    embed.add_field(name="At play", value=player_data.at_play, inline=True)
    embed.add_field(name="Profit", value=player_data.profit, inline=True)

    await ctx.send(embed=embed)
