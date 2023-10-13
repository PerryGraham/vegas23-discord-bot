import discord
from discord.ext import commands
from games.roulette import bet
from utils import general_commands
from games import steps
from games import russian_roulette

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
bot.add_command(russian_roulette.rbet)

bot.run(token)
