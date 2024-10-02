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
    # authenticate_yahoo,
)


print(get_injury_report())
