# OUTDATED AND NEED REFACTOR


@bot.command(brief="craps", pass_context=True)
async def craps(ctx):
    db = utils.get_db()

    craps_state = db.get("craps", {"point": 0, "bets": {}})

    embed = discord.Embed(
        title="Craps table summary",
        color=discord.Color.green(),
    )
    if craps_state["point"] == 0:
        embed.add_field(
            name="point",
            value="Has not been set. !crapsbet [wager] [bet_type] to play",
            inline=False,
        )
    else:
        embed.add_field(name="point", value=craps_state["point"], inline=False)

    for player, bet in craps_state["bets"].items():
        embed.add_field(
            name=player, value=f"{str(bet['wager'])} on {bet['line']}", inline=False
        )

    await ctx.send(embed=embed)


@bot.command(brief="craps", pass_context=True)
async def shoot(ctx):
    player_name = str(ctx.message.author.name)
    db = utils.get_db()

    craps_state = db.get("craps", {"point": 0, "bets": {}})

    d1, d2 = randint(1, 6), randint(1, 6)
    dice_sum = d1 + d2

    embed = discord.Embed(
        title=f"{utils.num_emoji(d1)}    {utils.num_emoji(d2)}",
        color=discord.Color.green(),
    )

    if craps_state["point"] == 0:
        if dice_sum in utils.craps("p"):
            # Pass wins
            embed.color = discord.Color.gold()
            embed.add_field(name="PASS WINS", value="")
            for player, bet in craps_state["bets"].items():
                if bet["line"] == "pass":
                    db[player]["at_play"] += bet["wager"] * 2
                    db[player]["on_table"] -= bet["wager"]
                    embed.add_field(name=player, value=f"Won {bet['wager']}")
                else:
                    db[player]["on_table"] -= bet["wager"]
                    embed.add_field(name=player, value=f"Lost {bet['wager']}")
            craps_state["bets"] = {}

        elif dice_sum in utils.craps("dp"):
            # Dont pass wins
            embed.color = discord.Color.red()
            embed.add_field(name="DONT PASS WINS", value="", inline=False)
            for player, bet in craps_state["bets"].items():
                if bet["line"] == "dont_pass":
                    if dice_sum == 12:
                        embed.add_field(
                            name=player, value=f"Push {bet['wager']}", inline=False
                        )
                        db[player]["at_play"] += bet["wager"]
                        db[player]["on_table"] -= bet["wager"]
                        continue
                    db[player]["at_play"] += bet["wager"] * 2
                    db[player]["on_table"] -= bet["wager"]
                    embed.add_field(
                        name=player, value=f"Won {bet['wager']}", inline=False
                    )
                else:
                    db[player]["on_table"] -= bet["wager"]
                    embed.add_field(
                        name=player, value=f"Lost {bet['wager']}", inline=False
                    )

            craps_state["bets"] = {}

        else:
            craps_state["point"] = dice_sum
            embed.add_field(
                name=f"Point set on {dice_sum}", value=f"Add your odds bets now."
            )

    else:
        # point on
        multi = utils.get_craps_multi(dice_sum)
        if craps_state["point"] == dice_sum:
            # pass wins
            embed.color = discord.Color.gold()
            embed.add_field(
                name="PASS WINS", value=f"point: {craps_state['point']}", inline=False
            )
            for player, bet in craps_state["bets"].items():
                if bet["line"] == "pass":
                    db[player]["at_play"] += (bet["wager"] * multi) + bet["wager"]
                    db[player]["on_table"] -= bet["wager"]
                    embed.add_field(
                        name=player, value=f"Won {bet['wager']*multi}", inline=False
                    )
                if bet["line"] == "dont_pass":
                    db[player]["on_table"] -= bet["wager"]
                    embed.add_field(
                        name=player, value=f"Lost {bet['wager']}", inline=False
                    )

            craps_state["point"] = 0
            craps_state["bets"] = {}

        elif dice_sum == 7:
            # dont pass wins
            embed.color = discord.Color.gold()
            embed.add_field(
                name="DONT PASS WINS",
                value=f"point: {craps_state['point']}",
                inline=False,
            )
            for player, bet in craps_state["bets"].items():
                if bet["line"] == "dont_pass":
                    db[player]["at_play"] += (bet["wager"] / multi) + bet["wager"]
                    db[player]["on_table"] -= bet["wager"]
                    embed.add_field(name=player, value=f"Won {bet['wager']/ multi}")
                if bet["line"] == "pass":
                    db[player]["on_table"] -= bet["wager"]
                    embed.add_field(name=player, value=f"Lost {bet['wager']}")

            craps_state["point"] = 0
            craps_state["bets"] = {}

        else:
            embed.add_field(name="Point", value=craps_state["point"], inline=False)
            embed.add_field(
                name="Shoot again",
                value=f"{craps_state['point']} or a 7 is needed to end the round",
                inline=False,
            )
            embed.color = discord.Color.blue()

    db["craps"] = craps_state
    utils.save_db(db)
    await ctx.send(embed=embed)


@bot.command(brief="craps", pass_context=True)
async def crapsbet(ctx, wager: int, line=None):
    author = str(ctx.message.author.name)
    db = utils.get_db()

    player_data = db.get(author, None)
    if player_data == None:
        await ctx.send("Add money with !add [amount]")
        return

    if line not in ["pass", "dont_pass", None]:
        await ctx.send("Bet line must be `pass` or `dont_pass`")
        return

    craps_state = db.get("craps", {"point": 0, "bets": {}})

    if line == None and craps_state["point"] == 0:
        await ctx.send(
            "When the point is off, you need to specify what your bet is: `pass` or `dont_pass`."
        )
        return

    if craps_state["point"] == 0:
        if author in craps_state["bets"].keys():
            await ctx.send("You Already placed a bet. Do !shoot to play")
            return
        craps_bet = {"wager": wager, "line": line, "odds_bet": 0}
        craps_state["bets"][author] = craps_bet

        player_data["at_play"] -= wager
        player_data["on_table"] += wager

    else:
        if author not in craps_state["bets"]:
            await ctx.send(
                "You can't place new bets while the point is on. Wait for the round to end"
            )
            return
        else:
            prev_bet = craps_state["bets"][author]

            if craps_state["point"] in [4, 10] and wager > (prev_bet["wager"] * 3):
                await ctx.send(
                    f"Max odds bet is X3. In your case: {prev_bet['wager'] * 3}"
                )
                return
            if craps_state["point"] in [5, 9] and wager > (prev_bet["wager"] * 4):
                await ctx.send(
                    f"Max odds bet is X4. In your case: {prev_bet['wager'] * 3}"
                )
                return
            if craps_state["point"] in [6, 8] and wager > (prev_bet["wager"] * 5):
                await ctx.send(
                    f"Max odds bet is X5. In your case: {prev_bet['wager'] * 3}"
                )
                return
            elif prev_bet["odds_bet"] == 1:
                await ctx.send(
                    f"Already placed an odds bet, your total on table is: {player_data['on_table']}"
                )
                return
            else:
                prev_bet["odds_bet"] = 1
                prev_bet["wager"] += wager
                player_data["at_play"] -= wager
                player_data["on_table"] += wager

    db["craps"] = craps_state
    utils.save_db(db)
    await ctx.send(f"Placed ${wager} on the table")
