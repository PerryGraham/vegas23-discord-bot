from discord.ext import commands
from random import randint
from utils import bot_utils as utils
from utils.schemas import Roulette

allowed_bets = ["BLACK", "B", "RED", "R", "GREEN", "G", "ODD", "EVEN"]


@commands.command(
    brief="Play roulette - (ex: !bet 100 black)",
    description="valid bet_types are [b, black, r, red, g, green, or any single number between 0-37]",
    pass_context=True,
)
async def bet(ctx, wager, bet):
    player = str(ctx.message.author.name)
    num = randint(0, 37)
    bet = bet.upper()
    print(num)

    all_users = utils.get_users()
    player_data = all_users.users[player]

    result = 0
    multi = 1

    resp = utils.verify_wager(wager, player_data)
    if resp is not None:
        await ctx.send(resp)
        return
    wager = int(wager)

    if num in Roulette.black:
        outcome = ["BLACK", "B"]
    elif num in Roulette.red:
        outcome = ["RED", "R"]
    elif num in Roulette.green:
        outcome = ["GREEN", "G"]
        multi = 17

    if num in Roulette.odd:
        outcome.append("ODD")
    elif num in Roulette.even:
        outcome.append("EVEN")

    if bet in outcome:
        result = 1

    try:
        if int(bet) not in range(38):
            await ctx.send("Straight bet must be between 0-37.")
            return

        if int(bet) == num:
            result = 1
            multi = 35
    except:
        if bet not in allowed_bets:
            await ctx.send("Bet type not supported.")
            return

    if result == 1:
        won = wager * multi
        player_data.at_play += won
        embed = utils.build_roulette_message(
            result=1,
            won=won,
            num=num,
            at_play=player_data.at_play,
        )

    else:
        player_data.at_play -= wager
        embed = utils.build_roulette_message(
            result=0,
            won=wager,
            num=num,
            at_play=player_data.at_play,
        )

    player_data.total_wagered += wager
    utils.save_users(users=all_users)

    await ctx.send(embed=embed)
