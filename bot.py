import discord
from random import randint
from utils import craps
from discord.ext import commands
from roulette import bet
import general_commands
import steps

with open("token.txt", "r") as f:
    token = f.read()
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


bot.add_command(bet)
bot.add_command(general_commands.bank)
bot.add_command(general_commands.daily)
bot.add_command(general_commands.add)
bot.add_command(general_commands.cashout)
bot.add_command(steps.step)
bot.add_command(steps.stop)


bot.run(token)
