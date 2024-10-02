import requests
import json
from datetime import datetime

from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo


def get_injury_report():
    # URL of the injury report
    url = "https://www.cbssports.com/nhl/injuries/"

    # Send a request to fetch the page content
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all 'TableBase-bodyTr' rows
    rows = soup.find_all("tr", class_="TableBase-bodyTr")

    player_names = [
        player.text.strip()
        for player in soup.find_all("span", class_="CellPlayerName--long")
    ]

    injury_objs = []

    # Loop through and format each row
    for row in rows:
        # Extract all table cells (td) within the row
        cells = row.find_all("td")

        player_name = cells[0].text.strip()

        position = cells[1].text.strip()

        designation_date = " ".join(cells[2].text.strip().split(" ")[1:])

        injury = cells[3].text.strip()

        injury_details = cells[4].text.strip()

        injury_obj = {
            "name": player_name,
            "position": position,
            "date": designation_date,
            "injury": injury,
            "details": injury_details,
        }

        injury_objs.append(injury_obj)

    # Replace dict values with corresponding strings
    for i, new_value in enumerate(player_names):
        injury_objs[i]["name"] = new_value

    # pop all objs that are not new
    injury_objs = [
        obj
        for obj in injury_objs
        if datetime.now(ZoneInfo("America/Los_Angeles")).date().replace(year=1900)
        == datetime.strptime(obj["date"], "%b %d").date()
    ]
    injury_objs = sorted(injury_objs, key=lambda d: d["name"])

    response = ""

    today = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%B %d, %Y")

    page_title = "NHL Injury Report"

    response += f"☠️ **{page_title} - {today}**\n\n"

    # response += "```"
    for obj in injury_objs:
        response += f"""{obj["name"]} ({obj["position"]}): {obj["injury"]} - {obj["details"]}\n"""

    # response += "```"

    if len(response) > 2000:
        response = f"☠️ **{page_title} - {today} - Condensed**;\n"
        response += "*Full injury report exceeds Discord message size limit. See source link for more info.*\n\n"

        # response += "```"
        for obj in injury_objs:
            response += f"""{obj["name"]} ({obj["position"]}): {obj["injury"]}\n"""

    response += f"\n*Source: <{url}>*\n"

    return response


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
    output += f"🥅 **{page_title}**\n\n"
    # output += "```"

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
    # output += "```"
    output += f"*Source: <{url}>*\n"

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
    output += f"🧑‍🧒‍🧒 **{page_title}**"
    # output += "```"

    for p in players:
        group_name = p["groupName"]

        if group_name not in output:
            output += "\n\n"
            output += group_name
            output += "\n"

        output += "\n"
        output += f'{p["name"]}'
        output += f' ({p["positionIdentifier"].upper()})'

    # output += "```"

    output += f"*Source: <{url}>*\n"

    return output
