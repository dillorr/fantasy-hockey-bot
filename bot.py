import os
import asyncio
import logging
from datetime import datetime, time
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

# Constants
TIMEZONE = "America/Los_Angeles"
GOALIES_CHANNEL_NAME = "starting-goalies"
INJURY_REPORT_CHANNEL_NAME = "injury-report"
GOALIES_SCHEDULE_TIME = time(11, 0)  # 11:00 AM
INJURY_REPORT_SCHEDULE_TIME = time(22, 0)  # 10:00 PM


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
        daily_scheduler.start()

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

    # SCHEDULED JOBS - Better approach using time-based scheduling
    last_sent_dates = {"goalies": None, "injuries": None}  # Track last sent dates to prevent duplicates

    async def _send_scheduled_report(report_type: str, data_func, channel_name: str):
        """Send a scheduled report with error handling and retries."""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                channel = bot.get_channel(text_channels[channel_name])
                if not channel:
                    logger.error(f"Channel '{channel_name}' not found")
                    return
                    
                content = data_func()
                await channel.send(content)
                logger.info(f"Successfully sent scheduled {report_type} report")
                return
                
            except Exception as e:
                retry_count += 1
                logger.warning(f"Attempt {retry_count} failed for {report_type} report: {e}")
                
                if retry_count >= max_retries:
                    logger.error(f"Failed to send {report_type} report after {max_retries} attempts")
                else:
                    # Wait 1 minute before retrying
                    await asyncio.sleep(60)

    @tasks.loop(minutes=5)  # Check every 5 minutes instead of every minute
    async def daily_scheduler():
        """Centralized scheduler for daily tasks."""
        try:
            current_time = datetime.now(ZoneInfo(TIMEZONE))
            current_date = current_time.date()
            
            # Check if it's time for starting goalies (11:00 AM)
            if (current_time.time() >= GOALIES_SCHEDULE_TIME and 
                current_time.time() < time(11, 5) and  # 5-minute window
                last_sent_dates["goalies"] != current_date):
                
                await _send_scheduled_report("goalies", get_starting_goalies, GOALIES_CHANNEL_NAME)
                last_sent_dates["goalies"] = current_date
                
            # Check if it's time for injury report (10:00 PM)
            if (current_time.time() >= INJURY_REPORT_SCHEDULE_TIME and 
                current_time.time() < time(22, 5) and  # 5-minute window
                last_sent_dates["injuries"] != current_date):
                
                await _send_scheduled_report("injuries", get_injury_report, INJURY_REPORT_CHANNEL_NAME)
                last_sent_dates["injuries"] = current_date
                
        except Exception as e:
            logger.error(f"Error in daily scheduler: {e}")

    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
