import json
from datetime import datetime
from typing import Dict, List, Any

import requests
from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo


def get_injury_report() -> str:
    """
    Fetch and format the current NHL injury report from CBS Sports.
    
    Returns:
        str: Formatted injury report with today's injuries only.
    """
    url = "https://www.cbssports.com/nhl/injuries/"

    # Send request to fetch the page content
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all injury report table rows
    rows = soup.find_all("tr", class_="TableBase-bodyTr")
    player_names = [
        player.text.strip()
        for player in soup.find_all("span", class_="CellPlayerName--long")
    ]

    injury_data: List[Dict[str, str]] = []

    # Process each row to extract injury information
    for row in rows:
        cells = row.find_all("td")
        
        if len(cells) >= 5:
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
            injury_data.append(injury_obj)

    # Update player names with properly formatted versions
    for i, new_name in enumerate(player_names):
        if i < len(injury_data):
            injury_data[i]["name"] = new_name

    # Filter for today's injuries only
    today_date = datetime.now(ZoneInfo("America/Los_Angeles")).date().replace(year=1900)
    todays_injuries = [
        obj for obj in injury_data
        if datetime.strptime(obj["date"], "%b %d").date() == today_date
    ]
    todays_injuries.sort(key=lambda d: d["name"])

    return _format_injury_response(todays_injuries, url)


def _format_injury_response(injuries: List[Dict[str, str]], source_url: str) -> str:
    """
    Format the injury data into a Discord-friendly message.
    
    Args:
        injuries: List of injury dictionaries
        source_url: URL of the injury report source
        
    Returns:
        str: Formatted injury report message
    """
    today = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%B %d, %Y")
    page_title = "NHL Injury Report"
    
    response = f"# ☠️ {page_title} - {today}\n\n"
    
    for injury in injuries:
        response += f"* {injury['name']} ({injury['position']}): {injury['injury']} - {injury['details']}\n"

    # Handle Discord message size limit
    if len(response) > 2000:
        response = f"# ☠️ {page_title} - {today} (Condensed)\n"
        response += "*Full injury report exceeds Discord message size limit. See source link for more info.*\n\n"
        
        for injury in injuries:
            response += f"* {injury['name']} ({injury['position']}): {injury['injury']}\n"

    response += f"\n*Source: <{source_url}>*\n"
    return response


def get_starting_goalies() -> str:
    """
    Fetch and format today's starting goalies from Daily Faceoff.
    
    Returns:
        str: Formatted starting goalies report
    """
    url = "https://www.dailyfaceoff.com/starting-goalies/"
    headers = {
        "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"
    }

    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    # Extract page title from meta tag
    page_title = "Starting Goalies"
    for tag in soup.find_all("meta"):
        if tag.get("property") == "og:title":
            page_title = tag.get("content", "").strip()
            break

    # Extract matchup data from JSON
    script_tag = soup.find("script", type="application/json")
    if not script_tag:
        return "Error: Could not find starting goalie data"
        
    try:
        matchups = json.loads(script_tag.text)["props"]["pageProps"]["data"]
    except (json.JSONDecodeError, KeyError):
        return "Error: Could not parse starting goalie data"

    return _format_goalies_response(matchups, page_title, url)


def _format_goalies_response(matchups: List[Dict[str, Any]], page_title: str, source_url: str) -> str:
    """
    Format the starting goalies data into a Discord-friendly message.
    
    Args:
        matchups: List of matchup dictionaries
        page_title: Title of the page
        source_url: URL of the source
        
    Returns:
        str: Formatted starting goalies message
    """
    output = f"# 🥅 {page_title}\n\n"

    for matchup in matchups:
        home_team = matchup.get("homeTeamName", "Unknown")
        away_team = matchup.get("awayTeamName", "Unknown")
        game_time = matchup.get("time", "TBD")
        
        home_goalie = matchup.get("homeGoalieName", "TBD")
        away_goalie = matchup.get("awayGoalieName", "TBD")
        
        home_status = matchup.get("homeNewsStrengthName") or "Unconfirmed"
        away_status = matchup.get("awayNewsStrengthName") or "Unconfirmed"

        output += f"{home_team} vs. {away_team} ({game_time})\n"
        output += f"{home_goalie} ({home_status}) vs. {away_goalie} ({away_status})\n\n"

    output += f"*Source: <{source_url}>*\n"
    return output


def get_line_combinations(team_name: str) -> str:
    """
    Fetch and format line combinations for a specific team from Daily Faceoff.
    
    Args:
        team_name: Team name formatted with hyphens (e.g., "san-jose-sharks")
        
    Returns:
        str: Formatted line combinations report
    """
    url = f"https://www.dailyfaceoff.com/teams/{team_name}/line-combinations/"
    headers = {
        "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"
    }

    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    # Extract page title from meta tag
    page_title = "Line Combinations"
    for tag in soup.find_all("meta"):
        if tag.get("property") == "og:title":
            page_title = tag.get("content", "").strip()
            break

    # Extract player data from JSON
    script_tag = soup.find("script", type="application/json")
    if not script_tag:
        return f"Error: Could not find line combination data for {team_name}"
        
    try:
        players = json.loads(script_tag.text)["props"]["pageProps"]["combinations"]["players"]
    except (json.JSONDecodeError, KeyError):
        return f"Error: Could not parse line combination data for {team_name}"

    today = datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%B %d, %Y")
    return _format_lines_response(players, page_title, today, url)


def _format_lines_response(players: List[Dict[str, Any]], page_title: str, date: str, source_url: str) -> str:
    """
    Format the line combinations data into a Discord-friendly message.
    
    Args:
        players: List of player dictionaries
        page_title: Title of the page
        date: Current date string
        source_url: URL of the source
        
    Returns:
        str: Formatted line combinations message
    """
    output = f"# 🧑‍🧒‍🧒 {page_title} - {date}\n\n"
    current_group = ""

    for player in players:
        group_name = player.get("groupName", "")
        player_name = player.get("name", "Unknown")
        position = player.get("positionIdentifier", "").upper()

        # Add group header if this is a new group
        if group_name != current_group:
            output += f"## {group_name}\n\n"
            current_group = group_name

        output += f"* {player_name} ({position})\n"

    output += f"\n*Source: <{source_url}>*\n"
    return output
