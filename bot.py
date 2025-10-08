import os
from datetime import datetime
from zoneinfo import ZoneInfo


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

        # automated jobs
        send_starting_goalies.start()
        send_injury_report.start()

    @bot.command(name="beep", brief="used to test to make sure the bot is online")
    async def beep(ctx):
        await ctx.send("boop")

    @bot.command(name="goalies", brief="Returns projected starting goalies for the day")
    async def get_starting_goalies_command(ctx):
        # await ctx.send("this command is temporarily disabled, sorry!")

        response = ""
        response += get_starting_goalies()
        response += f"\n<@{ctx.message.author.id}>"

        await ctx.send(response)

    @bot.command(name="injuries", brief="Returns injury report for the day")
    async def get_injury_report_command(ctx):
        # await ctx.send("this command is temporarily disabled, sorry!")

        response = ""
        response += get_injury_report()
        response += f"\n<@{ctx.message.author.id}>"

        await ctx.send(response)

    @bot.command(name="lines", brief="Returns current starting lineup for a team")
    async def get_lines_command(ctx, *args):
        # await ctx.send("this command is temporarily disabled, sorry!")

        team_name = "-".join([a.lower() for a in args])

        response = ""
        response += get_line_combinations(team_name)
        response += f"\n<@{ctx.message.author.id}>"

        await ctx.send(response)

    # EVENTS
    @bot.event
    async def on_command_error(ctx, error):

        if isinstance(error, commands.MissingRequiredArgument):
            response = f'Missing required argument: "{error.param}"'
        elif isinstance(error, commands.BadArgument):
            response = "Could not parse commands argument"
        else:
            print(error)
            response = f'Whoops! Something went wrong with "{ctx.message.content}".'

        await ctx.send(response)

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
