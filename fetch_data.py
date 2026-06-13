"""
fetch_data.py — Fetches FIFA World Cup 2026 data from api-football.com
and writes /data/worldcup.json for the static HTML to consume.

Called by GitHub Actions every minute during match windows.
Requires env var: RAPIDAPI_KEY
"""

import os
import json
import requests
from datetime import datetime, timezone

API_KEY = os.environ.get("RAPIDAPI_KEY", "")
BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"
HEADERS = {
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
    "x-rapidapi-key": API_KEY,
}

# FIFA World Cup 2026 league ID in api-football.com
WC_LEAGUE_ID = 1  # Confirm this ID in your RapidAPI dashboard; WC 2022 was 1
WC_SEASON = 2026


def api_get(endpoint, params=None):
    try:
        r = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS, params=params, timeout=10)
        r.raise_for_status()
        return r.json().get("response", [])
    except Exception as e:
        print(f"  ERROR {endpoint}: {e}")
        return []


def fetch_standings():
    data = api_get("standings", {"league": WC_LEAGUE_ID, "season": WC_SEASON})
    if not data:
        return []
    groups = []
    for entry in data:
        for league_data in entry.get("league", {}).get("standings", []):
            group_name = league_data[0].get("group", "Grupo ?") if league_data else "?"
            teams = []
            for t in league_data:
                teams.append({
                    "rank": t.get("rank"),
                    "team": t["team"]["name"],
                    "team_id": t["team"]["id"],
                    "logo": t["team"]["logo"],
                    "played": t["all"]["played"],
                    "win": t["all"]["win"],
                    "draw": t["all"]["draw"],
                    "lose": t["all"]["lose"],
                    "gf": t["all"]["goals"]["for"],
                    "ga": t["all"]["goals"]["against"],
                    "gd": t["goalsDiff"],
                    "points": t["points"],
                    "form": t.get("form", ""),
                    "description": t.get("description", ""),
                })
            groups.append({"group": group_name, "teams": teams})
    return groups


def fetch_live_fixtures():
    data = api_get("fixtures", {"league": WC_LEAGUE_ID, "season": WC_SEASON, "live": "all"})
    return parse_fixtures(data)


def fetch_today_fixtures():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data = api_get("fixtures", {"league": WC_LEAGUE_ID, "season": WC_SEASON, "date": today})
    return parse_fixtures(data)


def fetch_recent_fixtures(last=10):
    data = api_get("fixtures", {
        "league": WC_LEAGUE_ID,
        "season": WC_SEASON,
        "last": last,
        "status": "FT-AET-PEN"
    })
    return parse_fixtures(data)


def fetch_upcoming_fixtures(next=10):
    data = api_get("fixtures", {
        "league": WC_LEAGUE_ID,
        "season": WC_SEASON,
        "next": next
    })
    return parse_fixtures(data)


def fetch_top_scorers():
    data = api_get("players/topscorers", {"league": WC_LEAGUE_ID, "season": WC_SEASON})
    scorers = []
    for entry in data[:10]:
        p = entry.get("player", {})
        s = entry.get("statistics", [{}])[0]
        scorers.append({
            "name": p.get("name"),
            "photo": p.get("photo"),
            "team": s.get("team", {}).get("name"),
            "team_logo": s.get("team", {}).get("logo"),
            "goals": s.get("goals", {}).get("total", 0),
            "assists": s.get("goals", {}).get("assists", 0),
            "appearances": s.get("games", {}).get("appearences", 0),
        })
    return scorers


def parse_fixtures(data):
    fixtures = []
    for f in data:
        fix = f.get("fixture", {})
        teams = f.get("teams", {})
        goals = f.get("goals", {})
        score = f.get("score", {})
        status = fix.get("status", {})
        league = f.get("league", {})
        fixtures.append({
            "id": fix.get("id"),
            "date": fix.get("date"),
            "venue": fix.get("venue", {}).get("name"),
            "city": fix.get("venue", {}).get("city"),
            "status_short": status.get("short"),
            "status_long": status.get("long"),
            "elapsed": status.get("elapsed"),
            "round": league.get("round"),
            "home": {
                "id": teams["home"]["id"],
                "name": teams["home"]["name"],
                "logo": teams["home"]["logo"],
                "winner": teams["home"].get("winner"),
                "goals": goals.get("home"),
            },
            "away": {
                "id": teams["away"]["id"],
                "name": teams["away"]["name"],
                "logo": teams["away"]["logo"],
                "winner": teams["away"].get("winner"),
                "goals": goals.get("away"),
            },
            "halftime": {
                "home": score.get("halftime", {}).get("home"),
                "away": score.get("halftime", {}).get("away"),
            },
        })
    return fixtures


def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Fetching World Cup 2026 data...")

    if not API_KEY:
        print("ERROR: RAPIDAPI_KEY env var not set.")
        return

    live = fetch_live_fixtures()
    print(f"  Live fixtures: {len(live)}")

    today = fetch_today_fixtures()
    print(f"  Today fixtures: {len(today)}")

    recent = fetch_recent_fixtures(last=20)
    print(f"  Recent fixtures: {len(recent)}")

    upcoming = fetch_upcoming_fixtures(next=15)
    print(f"  Upcoming fixtures: {len(upcoming)}")

    standings = fetch_standings()
    print(f"  Groups fetched: {len(standings)}")

    scorers = fetch_top_scorers()
    print(f"  Top scorers: {len(scorers)}")

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "has_live": len(live) > 0,
        "live": live,
        "today": today,
        "recent": recent,
        "upcoming": upcoming,
        "standings": standings,
        "top_scorers": scorers,
    }

    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "worldcup.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"  Saved to {out_path}")
    print("Done.")


if __name__ == "__main__":
    main()
