import xmltodict

from yahoo_oauth import OAuth2


# returns team info given team key
def get_team(team_key: str, oauth: OAuth2, config: dict) -> str:
    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    url = f"{config['resource']['team']}{team_key}"
    response_dict = xmltodict.parse(oauth.session.get(url=url).content)[
        "fantasy_content"
    ]
    team = response_dict["team"]

    output = parse_team(team=team)

    return output


# given team dict from get_team, parse and return string
def parse_team(team: dict) -> str:
    output = ""
    output += f"**{team['name']} - Team Info**\n"
    output += f"Manager: {team['managers']['manager']['nickname']}\n"
    output += f"Draft position: {team['draft_position']}\n"
    output += f"Waiver priority: {team['waiver_priority']}\n"
    output += f"Moves: {team['number_of_moves']}\n"
    output += f"Trades: {team['number_of_trades']}\n"

    return output
