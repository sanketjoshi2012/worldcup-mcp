import json
import urllib.request
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("WorldCupMCP", log_level="ERROR")

DATA_URL = "https://raw.githubusercontent.com/openfootball/world-cup.json/master/2026/worldcup.json"


def fetch_data() -> dict:
    with urllib.request.urlopen(DATA_URL) as response:
        return json.loads(response.read())


@mcp.tool()
def get_todays_matches() -> str:
    """Get all FIFA World Cup 2026 matches happening today with scores and goals."""
    data = fetch_data()
    today = datetime.now().strftime("%Y-%m-%d")

    results = []
    for match in data.get("matches", []):
        if match.get("date") != today:
            continue

        home = match["team1"]
        away = match["team2"]
        score = match.get("score", {})
        ft = score.get("ft")

        if ft:
            result = f"{home} {ft[0]}-{ft[1]} {away} (FT)"
            goals1 = [f"{g['name']} {g['minute']}'" for g in match.get("goals1", [])]
            goals2 = [f"{g['name']} {g['minute']}'" for g in match.get("goals2", [])]
            if goals1 or goals2:
                result += f"\n  {home}: {', '.join(goals1) or 'No goals'}"
                result += f"\n  {away}: {', '.join(goals2) or 'No goals'}"
        else:
            time = match.get("time", "TBD")
            result = f"{home} vs {away} — {time}"

        round_name = match.get("round", "")
        group = match.get("group", "")
        stage = group or round_name
        results.append(f"[{stage}] {result}")

    if not results:
        return f"No World Cup matches found for today ({today})."
    return "\n\n".join(results)


@mcp.tool()
def get_standings() -> str:
    """Get FIFA World Cup 2026 group stage standings."""
    data = fetch_data()
    groups: dict = {}

    for match in data.get("matches", []):
        group = match.get("group")
        if not group:
            continue
        score = match.get("score", {}).get("ft")
        if not score:
            continue

        home, away = match["team1"], match["team2"]
        g1, g2 = score

        for team in [home, away]:
            if group not in groups:
                groups[group] = {}
            if team not in groups[group]:
                groups[group][team] = {"P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "Pts": 0}

        groups[group][home]["P"] += 1
        groups[group][away]["P"] += 1
        groups[group][home]["GF"] += g1
        groups[group][home]["GA"] += g2
        groups[group][away]["GF"] += g2
        groups[group][away]["GA"] += g1

        if g1 > g2:
            groups[group][home]["W"] += 1
            groups[group][home]["Pts"] += 3
            groups[group][away]["L"] += 1
        elif g2 > g1:
            groups[group][away]["W"] += 1
            groups[group][away]["Pts"] += 3
            groups[group][home]["L"] += 1
        else:
            groups[group][home]["D"] += 1
            groups[group][away]["D"] += 1
            groups[group][home]["Pts"] += 1
            groups[group][away]["Pts"] += 1

    output = []
    for group_name in sorted(groups.keys()):
        teams = groups[group_name]
        output.append(f"\n{group_name}")
        output.append(f"{'Team':<25} {'P':>3} {'W':>3} {'D':>3} {'L':>3} {'GF':>4} {'GA':>4} {'Pts':>4}")
        for team, s in sorted(teams.items(), key=lambda x: -x[1]["Pts"]):
            output.append(f"{team:<25} {s['P']:>3} {s['W']:>3} {s['D']:>3} {s['L']:>3} {s['GF']:>4} {s['GA']:>4} {s['Pts']:>4}")

    return "\n".join(output) if output else "No standings available yet."


@mcp.tool()
def get_match_result(team1: str, team2: str) -> str:
    """Get the result and goals for a specific World Cup match between two teams."""
    data = fetch_data()

    for match in data.get("matches", []):
        h, a = match["team1"].lower(), match["team2"].lower()
        if (team1.lower() in h or team1.lower() in a) and (team2.lower() in h or team2.lower() in a):
            home, away = match["team1"], match["team2"]
            score = match.get("score", {}).get("ft")
            date = match.get("date", "Unknown date")
            round_name = match.get("round", match.get("group", ""))

            if score:
                goals1 = [f"{g['name']} {g['minute']}'" for g in match.get("goals1", [])]
                goals2 = [f"{g['name']} {g['minute']}'" for g in match.get("goals2", [])]
                result = f"{home} {score[0]}-{score[1]} {away}\n"
                result += f"Date: {date} | Stage: {round_name}\n"
                result += f"Goals {home}: {', '.join(goals1) or 'None'}\n"
                result += f"Goals {away}: {', '.join(goals2) or 'None'}"
            else:
                result = f"{home} vs {away} — not played yet\nDate: {date} | Stage: {round_name}"
            return result

    return f"No match found between {team1} and {team2}."


@mcp.tool()
def get_all_results(round_name: str = "") -> str:
    """Get all World Cup 2026 results. Optionally filter by round like 'Quarter-final' or 'Group A'."""
    data = fetch_data()
    results = []

    for match in data.get("matches", []):
        stage = match.get("group", match.get("round", ""))
        if round_name and round_name.lower() not in stage.lower():
            continue
        score = match.get("score", {}).get("ft")
        home, away = match["team1"], match["team2"]
        date = match.get("date", "")
        if score:
            results.append(f"{date} [{stage}] {home} {score[0]}-{score[1]} {away}")
        else:
            results.append(f"{date} [{stage}] {home} vs {away} (upcoming)")

    return "\n".join(results) if results else f"No results found for '{round_name}'."


@mcp.prompt()
def summarize_match(team1: str, team2: str) -> str:
    """Write an exciting journalist-style summary of a World Cup match."""
    return f"Get the result for the World Cup match between {team1} and {team2}, then write an exciting match summary as if you're a sports journalist covering the FIFA World Cup 2026. Include the scoreline, goalscorers, and the significance of the result."


if __name__ == "__main__":
    mcp.run(transport="stdio")
