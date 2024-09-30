import xmltodict

from yahoo_oauth import OAuth2


# get current scores
def get_scores(oauth: OAuth2, league_config: dict) -> str:
    url = f"""https://fantasysports.yahooapis.com/fantasy/v2/league/{league_config["key"]}/scoreboard"""

    response_dict = xmltodict.parse(oauth.session.get(url=url).content)[
        "fantasy_content"
    ]["league"]["scoreboard"]

    matchups = response_dict["matchups"]["matchup"]

    output = ""
    output += f"**Matchups - Current Scores:**"
    output += parse_scores(matchups)

    return output


def parse_scores(matchups: list) -> str:
    default_padding = 5

    team_names = []
    scores = []

    for i, m in enumerate(matchups):
        t1 = m["teams"]["team"][0]
        t2 = m["teams"]["team"][1]

        matchup = {
            t1["name"]: t1["team_points"]["total"],
            t2["name"]: t2["team_points"]["total"],
        }

        for tn in list(matchup.keys()):
            team_names.append(tn)

        scores.append(matchup)

    # since discord doesn't support tables, create uniform row position of score
    longest_name = sorted(team_names, key=len, reverse=True)[0]

    output = ""
    output += "```"

    for score in scores:
        for key, value in score.items():
            output += f"{key} "
            if key != longest_name:
                for _ in range(len(longest_name) - len(key) + default_padding):
                    output += " "
            else:
                for _ in range(default_padding):
                    output += " "

            output += f"{value}\n"

        output += "\n"
    output += "```"

    return output


def get_matchups(oauth: OAuth2, league_config: dict) -> str:
    url = f"""https://fantasysports.yahooapis.com/fantasy/v2/league/{league_config["key"]}/scoreboard"""
    response_dict = xmltodict.parse(oauth.session.get(url=url).content)
    current_week = response_dict["fantasy_content"]["league"]["current_week"]
    matchups = response_dict["fantasy_content"]["league"]["scoreboard"]["matchups"][
        "matchup"
    ]

    output = f"**Matchups - Week {current_week}**"

    output += "```\n"

    for matchup in matchups:
        for team in matchup["teams"]["team"]:
            output += f"{team['name']}\n"
        output += "\n"

    output += "```"

    return output
