import xmltodict

from yahoo_oauth import OAuth2


# returns dictionary of roster given team key
def get_roster(team_key: str, oauth: OAuth2, config: dict) -> str:
    url = f"{config['resource']['team']}{team_key}/roster/players"

    response_dict = xmltodict.parse(oauth.session.get(url=url).content)[
        "fantasy_content"
    ]["team"]
    roster = response_dict["roster"]

    output = "```"

    output += parse_roster(roster=roster)

    output += "```"

    return output


def parse_roster(roster: dict) -> str:
    output = ""
    for player in roster["players"]["player"]:
        output += (
            f"[{player['selected_position']['position']}] "
            f"{player['name']['full']} ({player['editorial_team_abbr']}) - {player['display_position']}\n"
        )

    return output
