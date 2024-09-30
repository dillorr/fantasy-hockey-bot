import requests
import json

from bs4 import BeautifulSoup


def get_starting_goalies() -> str:
    url = "https://www.dailyfaceoff.com/starting-goalies/"

    headers = {
        "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"
    }

    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, "html.parser")

    # get title
    page_title = "Starting Goalies"

    for tag in soup.find_all("meta"):
        if tag.get("property", None) == "og:title":
            page_title = tag.get("content", None).strip()
        # elif tag.get("property", None) == "og:url":
        #     url = tag.get("content", None).strip()

    matchups = json.loads(soup.find("script", type="application/json").text)["props"][
        "pageProps"
    ]["data"]

    output = ""
    output += f"**{page_title}**"
    output += "```"
    output += "\n\n"

    for m in matchups:
        # print(m, '\n')
        output += f'{m["homeTeamName"]}'
        output += " vs. "
        output += f'{m["awayTeamName"]}'
        output += f' ({m["time"]})'
        output += "\n"
        output += f'{m["homeGoalieName"]}'

        home_status = m["homeNewsStrengthName"]
        if home_status is None:
            home_status = "Unconfirmed"

        output += f" ({home_status}), "
        output += f'{m["awayGoalieName"]}'
        away_status = m["awayNewsStrengthName"]

        if away_status is None:
            away_status = "Unconfirmed"

        output += f" ({away_status})"
        output += "\n\n"

    # print(output)
    # print(matchups)
    output += "```"
    output += f"Source: <{url}>\n"

    return output


def get_line_combinations(team_name: str) -> str:
    url = f"https://www.dailyfaceoff.com/teams/{team_name}/line-combinations/"
    headers = {
        "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"
    }

    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, "html.parser")

    # get title
    page_title = "Starting Goalies"

    for tag in soup.find_all("meta"):
        if tag.get("property", None) == "og:title":
            page_title = tag.get("content", None).strip()
        # elif tag.get("property", None) == "og:url":
        #     url = tag.get("content", None).strip()

    players = json.loads(soup.find("script", type="application/json").text)["props"][
        "pageProps"
    ]["combinations"]["players"]

    output = ""
    output += f"**{page_title}**"
    output += "```"

    for p in players:
        group_name = p["groupName"]

        if group_name not in output:
            output += "\n\n"
            output += group_name
            output += "\n"

        output += "\n"
        output += f'{p["name"]}'
        output += f' ({p["positionIdentifier"].upper()})'

    output += "```"

    output += f"Source: <{url}>\n"

    return output
