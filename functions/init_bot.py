import discord
from discord.ext import commands


def init_bot() -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True

    help_command = commands.DefaultHelpCommand(no_category="Commands", dm_help=False)

    bot = commands.Bot(
        command_prefix="!",
        intents=intents,
        help_command=help_command,
    )

    return bot
