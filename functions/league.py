import xmltodict

from yahoo_oauth import OAuth2


# returns dictionary of league info
def get_league(oauth: OAuth2, league_config: dict) -> str:
    url = f"""https://fantasysports.yahooapis.com/fantasy/v2/league/{league_config["key"]}"""
    response_dict = xmltodict.parse(oauth.session.get(url=url).content)[
        "fantasy_content"
    ]

    league = response_dict["league"]

    output = parse_league(league=league)

    return output


def parse_league(league: dict) -> str:
    output = ""
    output += f"**{league['name']} - League Info**\n"
    output += f"Season: {league['season']}\n"
    output += f"Teams: {league['num_teams']}\n"
    output += f"Week: {league['current_week']}\n\n"

    return output


# returns dictionary of teams in league
def get_teams(oauth: OAuth2, league_config: dict) -> dict:
    url = f"""https://fantasysports.yahooapis.com/fantasy/v2/league/{league_config["key"]}/teams"""
    response_dict = xmltodict.parse(oauth.session.get(url=url).content)[
        "fantasy_content"
    ]

    output = response_dict["league"]["teams"]

    return output


# returns dictionary of team_name: team_key
def get_team_keys(oauth: OAuth2, league_config: dict) -> dict:
    team_keys = {}

    for team in get_teams(oauth=oauth, league_config=league_config)["team"]:
        team_keys[team["name"]] = team["team_key"]

    return team_keys


def get_standings(oauth: OAuth2, league_config: dict) -> str:
    url = f"""https://fantasysports.yahooapis.com/fantasy/v2/league/{league_config["key"]}/standings"""
    response_dict = xmltodict.parse(oauth.session.get(url=url).content)[
        "fantasy_content"
    ]

    output = f"**{response_dict['league']['name']} - Standings**"

    standings = response_dict["league"]["standings"]["teams"]["team"]

    output += "```"
    output += parse_standings(standings)
    output += "```"

    return output


def parse_standings(standings: list) -> str:
    standings_dict = {}

    for team in standings:
        standings_dict[team["name"]] = {
            "standing": team["team_standings"]["rank"],
            "wins": team["team_standings"]["outcome_totals"]["wins"],
            "losses": team["team_standings"]["outcome_totals"]["losses"],
            "ties": team["team_standings"]["outcome_totals"]["ties"],
            "pct": team["team_standings"]["outcome_totals"]["percentage"],
            "points": team["team_points"]["total"],
        }

    standings_order = {}

    for key, value in standings_dict.items():
        standings_order[key] = value["standing"]

    output = ""

    for key in dict(
        sorted(standings_order.items(), key=lambda item: int(item[1]))
    ).keys():
        output += f"{standings_dict[key]['standing']}. {key}: {standings_dict[key]['wins']}-{standings_dict[key]['losses']}-{standings_dict[key]['ties']} ({standings_dict[key]['points']})\n"

    return output
