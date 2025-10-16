import os
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks

from functions import (
    init_bot,
    get_line_combinations,
    get_starting_goalies,
    get_injury_report,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants
TIMEZONE = "America/Los_Angeles"
GOALIES_SCHEDULE_HOUR = 11
INJURY_REPORT_SCHEDULE_HOUR = 22
GOALIES_CHANNEL_NAME = "starting-goalies"
INJURY_REPORT_CHANNEL_NAME = "injury-report"


def main():
    """Initialize and run the Discord fantasy hockey bot."""
    bot = init_bot()

    # Dictionary for storing active text channels in server and their channel IDs
    text_channels = {}

    @bot.listen()
    async def on_ready():
        """Handle bot ready event - sync commands and start scheduled tasks."""
        # Get Discord guild
        guild = bot.guilds[0]

        text_channels.update({channel.name: channel.id for channel in guild.text_channels})

        # Sync slash commands
        try:
            synced = await bot.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

        # Start automated jobs
        send_starting_goalies.start()
        send_injury_report.start()

    @bot.tree.command(name="beep", description="Test to make sure the bot is online")
    async def beep(interaction: discord.Interaction):
        """Simple test command to verify bot connectivity."""
        await interaction.response.send_message("boop")

    def _build_response_with_mention(content: str, user_id: int) -> str:
        """Build a response message with user mention."""
        return f"{content}\n<@{user_id}>"

    @bot.tree.command(name="goalies", description="Returns projected starting goalies for the day")
    async def get_starting_goalies_command(interaction: discord.Interaction):
        """Get today's projected starting goalies."""
        try:
            content = get_starting_goalies()
            response = _build_response_with_mention(content, interaction.user.id)
            await interaction.response.send_message(response)
        except Exception as e:
            logger.error(f"Error in goalies command: {e}")
            await interaction.response.send_message("Sorry, I couldn't fetch the starting goalies right now. Please try again later.")

    @bot.tree.command(name="injuries", description="Returns injury report for the day")
    async def get_injury_report_command(interaction: discord.Interaction):
        """Get today's NHL injury report."""
        try:
            content = get_injury_report()
            response = _build_response_with_mention(content, interaction.user.id)
            await interaction.response.send_message(response)
        except Exception as e:
            logger.error(f"Error in injuries command: {e}")
            await interaction.response.send_message("Sorry, I couldn't fetch the injury report right now. Please try again later.")

    @bot.tree.command(name="lines", description="Returns current starting lineup for a team")
    async def get_lines_command(interaction: discord.Interaction, team_name: str):
        """Get current starting lineup for a specified team."""
        try:
            # Convert the team name to the expected format (lowercase with hyphens)
            formatted_team_name = team_name.lower().replace(" ", "-")
            
            content = get_line_combinations(formatted_team_name)
            response = _build_response_with_mention(content, interaction.user.id)
            await interaction.response.send_message(response)
        except Exception as e:
            logger.error(f"Error in lines command for team '{team_name}': {e}")
            await interaction.response.send_message(f"Sorry, I couldn't fetch the line combinations for '{team_name}'. Please check the team name and try again.")

    # SCHEDULED JOBS
    @tasks.loop(minutes=1)
    async def send_starting_goalies():
        """Send starting goalies to designated channel at scheduled time."""
        channel = bot.get_channel(text_channels[GOALIES_CHANNEL_NAME])
        current_time = datetime.now(ZoneInfo(TIMEZONE))

        if current_time.hour == GOALIES_SCHEDULE_HOUR and current_time.minute == 0:
            try:
                content = get_starting_goalies()
                await channel.send(content)
                logger.info("Successfully sent scheduled starting goalies report")
            except Exception as e:
                logger.error(f"Error sending scheduled starting goalies: {e}")

    @tasks.loop(minutes=1)
    async def send_injury_report():
        """Send injury report to designated channel at scheduled time."""
        channel = bot.get_channel(text_channels[INJURY_REPORT_CHANNEL_NAME])
        current_time = datetime.now(ZoneInfo(TIMEZONE))

        if current_time.hour == INJURY_REPORT_SCHEDULE_HOUR and current_time.minute == 0:
            try:
                content = get_injury_report()
                await channel.send(content)
                logger.info("Successfully sent scheduled injury report")
            except Exception as e:
                logger.error(f"Error sending scheduled injury report: {e}")

    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
