import os
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks, commands


from functions import (
    init_bot,
    get_line_combinations,
    get_starting_goalies,
    get_injury_report,
)


def main():
    bot = init_bot()

    # dict for storing the active text channels in server and their channel ids
    text_channels = {}

    @bot.listen()
    async def on_ready():
        # get discord guild
        guild = bot.guilds[0]

        text_channels = {channel.name: channel.id for channel in guild.text_channels}

        # Sync slash commands
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

        # automated jobs
        send_starting_goalies.start()
        send_injury_report.start()

    @bot.tree.command(name="beep", description="Test to make sure the bot is online")
    async def beep(interaction: discord.Interaction):
        await interaction.response.send_message("boop")

    @bot.tree.command(name="goalies", description="Returns projected starting goalies for the day")
    async def get_starting_goalies_command(interaction: discord.Interaction):
        # await interaction.response.send_message("this command is temporarily disabled, sorry!")

        response = ""
        response += get_starting_goalies()
        response += f"\n<@{interaction.user.id}>"

        await interaction.response.send_message(response)

    @bot.tree.command(name="injuries", description="Returns injury report for the day")
    async def get_injury_report_command(interaction: discord.Interaction):
        # await interaction.response.send_message("this command is temporarily disabled, sorry!")

        response = ""
        response += get_injury_report()
        response += f"\n<@{interaction.user.id}>"

        await interaction.response.send_message(response)

    @bot.tree.command(name="lines", description="Returns current starting lineup for a team")
    async def get_lines_command(interaction: discord.Interaction, team_name: str):
        # await interaction.response.send_message("this command is temporarily disabled, sorry!")

        # Convert the team name to the expected format (lowercase with hyphens)
        formatted_team_name = team_name.lower().replace(" ", "-")

        response = ""
        response += get_line_combinations(formatted_team_name)
        response += f"\n<@{interaction.user.id}>"

        await interaction.response.send_message(response)

    # SCHEDULED JOBS
    @tasks.loop(minutes=1)
    async def send_starting_goalies():
        channel = bot.get_channel(text_channels["starting-goalies"])

        t = datetime.now(ZoneInfo("America/Los_Angeles"))

        if t.hour == 11 and t.minute == 0:
            response = ""
            response += get_starting_goalies()

            await channel.send(response)

    @tasks.loop(minutes=1)
    async def send_injury_report():
        channel = bot.get_channel(text_channels["injury-report"])

        t = datetime.now(ZoneInfo("America/Los_Angeles"))

        if t.hour == 22 and t.minute == 0:
            response = ""
            response += get_injury_report()

            await channel.send(response)

    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
