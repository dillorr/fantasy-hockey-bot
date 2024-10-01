import json
import os

# import logging

from datetime import datetime, timezone, timedelta
from discord.ext import tasks, commands
from zoneinfo import ZoneInfo

from functions import (
    init_bot,
    # get_standings,
    # get_scores,
    # get_matchups,
    get_line_combinations,
    get_starting_goalies,
    get_injury_report,
    # autƒhenticate_yahoo,
)


def configure():
    # logging.basicConfig(
    #     filename="app.log",
    #     filemode="a",
    #     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    #     datefmt="%Y-%m-%d %H:%M:%S",
    #     level=logging.DEBUG,
    # )

    with open(".config/league.json", "r") as f:
        league_config = json.load(f)

    bot = init_bot()

    return league_config, bot


def main():
    league_config, bot = configure()

    # dict for storing the active text channels in server and their channel ids
    text_channels = {}

    @bot.listen()
    async def on_ready():
        # get discord guilds data
        guild = bot.guilds[0]

        for channel in guild.text_channels:
            text_channels[channel.name] = channel.id

        # automated jobs
        send_starting_goalies.start()
        send_injury_report.start()

    @bot.command(name="beep", brief="used to test to make sure the bot is online")
    async def beep(ctx):
        await ctx.send("boop")

    @bot.command(name="standings", brief="Returns standings")
    async def get_standings_command(ctx):
        await ctx.send("this command is temporarily disabled, sorry!")
        # logging.debug(f"@{ctx.message.author.name}: {ctx.message.content}")

        # oauth = authenticate_yahoo()

        # response = ""

        # response += get_standings(oauth=oauth, league_config=league_config)
        # response += f"\n<@{ctx.message.author.id}>"

        # await ctx.send(response)

    @bot.command(name="scores", brief="Returns current scores for all matchups")
    async def get_scores_command(ctx):
        await ctx.send("this command is temporarily disabled, sorry!")
        # logging.debug(f"@{ctx.message.author.name}: {ctx.message.content}")

        # oauth = authenticate_yahoo()

        # response = ""

        # response += get_scores(oauth=oauth, league_config=league_config)
        # response += f"\n<@{ctx.message.author.id}>"

        # await ctx.send(response)

    @bot.command(name="goalies", brief="Returns projected starting goalies for the day")
    async def get_starting_goalies_command(ctx):
        await ctx.send("this command is temporarily disabled, sorry!")
        # logging.debug(f"@{ctx.message.author.name}: {ctx.message.content}")

        # response = ""

        # response += get_starting_goalies()
        # response += f"\n<@{ctx.message.author.id}>"

        # await ctx.send(response)

    @bot.command(name="injuries", brief="Returns injury report for the day")
    async def get_injury_report_command(ctx):
        # await ctx.send("this command is temporarily disabled, sorry!")
        # logging.debug(f"@{ctx.message.author.name}: {ctx.message.content}")

        response = ""

        response += get_injury_report()
        response += f"\n<@{ctx.message.author.id}>"

        await ctx.send(response)

    @bot.command(name="lines", brief="Returns current starting lineup for a team")
    async def get_lines_command(ctx, *args):
        # await ctx.send("this command is temporarily disabled, sorry!")
        # logging.debug(f"@{ctx.message.author.name}: {ctx.message.content}")

        team_name = "-".join([a.lower() for a in args])

        response = ""

        response += get_line_combinations(team_name)
        response += f"\n<@{ctx.message.author.id}>"

        await ctx.send(response)

    # EVENTS
    @bot.event
    async def on_command_error(ctx, error):
        # logging.debug(f"@{ctx.message.author.name}: {ctx.message.content}")
        # logging.error(error)

        if isinstance(error, commands.MissingRequiredArgument):
            response = f'Missing required argument: "{error.param}"'
        elif isinstance(error, commands.BadArgument):
            response = "Could not parse commands argument"
        else:
            print(error)
            response = f'I don\'t know what "{ctx.message.content}" means.'

        await ctx.send(response)

    # SCHEDULED JOBS
    @tasks.loop(minutes=1)
    async def send_starting_goalies():
        channel = bot.get_channel(text_channels["starting-goalies"])

        t = datetime.now(ZoneInfo("America/Los_Angeles"))

        # oauth = authenticate_yahoo()

        if t.hour == 12 and t.minute == 0:
            response = ""

            # DISABLED
            # if beginning of new week
            # if t.weekday() == 0:
            #     response += get_matchups(oauth=oauth, league_config=league_config)
            #     response += "\n"
            #     response += get_standings(oauth=oauth, league_config=league_config)

            # else:
            #     response += get_scores(oauth=oauth, league_config=league_config)

            # always list starting goalies
            # response += "\n"
            response += get_starting_goalies()

            await channel.send(response)

    @tasks.loop(minutes=1)
    async def send_injury_report():
        channel = bot.get_channel(text_channels["injury-report"])

        t = datetime.now(ZoneInfo("America/Los_Angeles"))

        # oauth = authenticate_yahoo()

        if t.hour == 22 and t.minute == 0:
            response = ""

            # DISABLED
            # if beginning of new week
            # if t.weekday() == 0:
            #     response += get_matchups(oauth=oauth, league_config=league_config)
            #     response += "\n"
            #     response += get_standings(oauth=oauth, league_config=league_config)

            # else:
            #     response += get_scores(oauth=oauth, league_config=league_config)

            # always list starting goalies
            # response += "\n"
            response += get_injury_report()

            await channel.send(response)

    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    main()
