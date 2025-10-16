import discord
from discord.ext import commands


def init_bot() -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True

    # We can remove the help_command since slash commands have built-in help
    bot = commands.Bot(
        command_prefix="!",  # Keep prefix for any remaining traditional commands if needed
        intents=intents,
        help_command=None,  # Disable traditional help since we're using slash commands
    )

    return bot
