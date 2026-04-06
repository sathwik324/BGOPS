"""
NBA Game Outcome Prediction System — ETL: Fetch Data
Fetches teams, player stats, schedule, and head-to-head data from nba_api.
Caches results as JSON in ./data_cache/.
"""

import os
import json
import time
import logging
import pandas as pd

from datetime import datetime, timedelta
from nba_api.stats.endpoints import LeagueStandings, LeagueDashPlayerStats, LeagueGameLog, ScoreboardV2

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SEASON = "2025-26"
DELAY = 1.2          # seconds between nba_api calls
RETRIES = 3          # max retry attempts per call
CACHE_DIR = "./data_cache"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def _ensure_cache_dir() -> None:
    """Create the cache directory if it doesn't exist."""
    os.makedirs(CACHE_DIR, exist_ok=True)


def _save_json(data: list[dict], filename: str) -> None:
    """Save a list of dicts to a JSON file in the cache directory."""
    filepath = os.path.join(CACHE_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    logger.info("Saved %d records to %s", len(data), filepath)


def _api_call_with_retry(endpoint_cls, **kwargs) -> pd.DataFrame:
    """
    Call an nba_api endpoint with retry logic and inter-request delay.
    Returns the first DataFrame from the endpoint results.
    """
    for attempt in range(1, RETRIES + 1):
        try:
            logger.info(
                "Calling %s (attempt %d/%d)...",
                endpoint_cls.__name__, attempt, RETRIES,
            )
            ep = endpoint_cls(**kwargs)
            time.sleep(DELAY)
            dfs = ep.get_data_frames()
            if dfs and len(dfs) > 0:
                return dfs[0]
            return pd.DataFrame()
        except Exception as exc:
            logger.warning(
                "Attempt %d failed for %s: %s",
                attempt, endpoint_cls.__name__, exc,
            )
            if attempt < RETRIES:
                wait = DELAY * attempt
                logger.info("Retrying in %.1f seconds...", wait)
                time.sleep(wait)
            else:
                logger.error("All %d attempts failed for %s", RETRIES, endpoint_cls.__name__)
                raise


# ---------------------------------------------------------------------------
# Fetch functions
# ---------------------------------------------------------------------------

def fetch_all_teams() -> list[dict]:
    """
    Fetch all NBA teams with current standings from LeagueStandings.
    Parses the L10 string "7-3" into last_10_wins / last_10_losses.
    """
    logger.info("Fetching all teams for season %s...", SEASON)
    df = _api_call_with_retry(
        LeagueStandings,
        season=SEASON,
        league_id="00",
        season_type="Regular Season",
    )

    if df.empty:
        logger.warning("No team standings data returned.")
        return []

    teams = []
    for _, row in df.iterrows():
        # Parse L10 record (e.g. "7-3")
        l10 = str(row.get("L10", "0-0"))
        try:
            parts = l10.split("-")
            l10_wins = int(parts[0])
            l10_losses = int(parts[1]) if len(parts) > 1 else 0
        except (ValueError, IndexError):
            l10_wins, l10_losses = 0, 0

        teams.append({
            "nba_team_id": int(row["TeamID"]),
            "name": str(row.get("TeamName", "")),
            "abbreviation": str(row.get("TeamAbbreviation", row.get("TeamSlug", ""))),
            "city": str(row.get("TeamCity", "")),
            "conference": str(row.get("Conference", "")),
            "division": str(row.get("Division", "")),
            "wins": int(row.get("WINS", row.get("W", 0))),
            "losses": int(row.get("LOSSES", row.get("L", 0))),
            "last_10_wins": l10_wins,
            "last_10_losses": l10_losses,
        })

    _save_json(teams, "teams.json")
    logger.info("Fetched %d teams.", len(teams))
    return teams


def fetch_player_stats() -> list[dict]:
    """
    Fetch per-game player statistics from LeagueDashPlayerStats.
    """
    logger.info("Fetching player stats for season %s...", SEASON)
    df = _api_call_with_retry(
        LeagueDashPlayerStats,
        season=SEASON,
        per_mode_detailed="PerGame",
        season_type_all_star="Regular Season",
    )

    if df.empty:
        logger.warning("No player stats data returned.")
        return []

    players = []
    for _, row in df.iterrows():
        players.append({
            "nba_player_id": int(row["PLAYER_ID"]),
            "nba_team_id": int(row.get("TEAM_ID", 0)),
            "full_name": str(row.get("PLAYER_NAME", "")),
            "position": str(row.get("POS", row.get("PLAYER_POSITION", ""))),
            "games_played": int(row.get("GP", 0)),
            "points_per_game": float(row.get("PTS", 0)),
            "assists_per_game": float(row.get("AST", 0)),
            "rebounds_per_game": float(row.get("REB", 0)),
            "steals_per_game": float(row.get("STL", 0)),
            "blocks_per_game": float(row.get("BLK", 0)),
            "minutes_per_game": float(row.get("MIN", 0)),
            "season": SEASON,
        })

    _save_json(players, "player_stats.json")
    logger.info("Fetched stats for %d players.", len(players))
    return players


def fetch_schedule() -> list[dict]:
    """
    Fetch the game schedule/results from LeagueGameLog.
    Two rows per game (one per team) are collapsed into a single match record.
    'vs.' indicates a home game; '@' indicates an away game.
    """
    logger.info("Fetching schedule for season %s...", SEASON)
    df = _api_call_with_retry(
        LeagueGameLog,
        season=SEASON,
        season_type_all_star="Regular Season",
        player_or_team_abbreviation="T",
    )

    if df.empty:
        logger.warning("No schedule data returned.")
        return []

    # Build a dict keyed by GAME_ID to merge two rows per game
    games: dict[str, dict] = {}

    for _, row in df.iterrows():
        game_id = str(row["GAME_ID"])
        matchup = str(row.get("MATCHUP", ""))
        team_id = int(row["TEAM_ID"])
        team_abbr = str(row.get("TEAM_ABBREVIATION", ""))
        wl = str(row.get("WL", ""))
        pts = int(row.get("PTS", 0))
        game_date = str(row.get("GAME_DATE", ""))[:10]  # YYYY-MM-DD

        if game_id not in games:
            games[game_id] = {
                "nba_game_id": game_id,
                "scheduled_date": game_date,
                "season": SEASON,
                "home_team_id": None,
                "away_team_id": None,
                "home_score": None,
                "away_score": None,
                "winner_nba_team_id": None,
                "status": "completed",
            }

        g = games[game_id]

        # Determine home/away from MATCHUP string
        if "vs." in matchup:
            g["home_team_id"] = team_id
            g["home_score"] = pts
            if wl == "W":
                g["winner_nba_team_id"] = team_id
        elif "@" in matchup:
            g["away_team_id"] = team_id
            g["away_score"] = pts
            if wl == "W":
                g["winner_nba_team_id"] = team_id

    schedule = list(games.values())
    _save_json(schedule, "schedule.json")
    logger.info("Fetched %d games.", len(schedule))
    return schedule


def fetch_head_to_head() -> list[dict]:
    """
    Compute head-to-head records from the cached schedule data.
    Enforces team_a_id < team_b_id convention.
    """
    logger.info("Computing head-to-head records from schedule...")

    schedule_path = os.path.join(CACHE_DIR, "schedule.json")
    if not os.path.exists(schedule_path):
        logger.warning("schedule.json not found. Run fetch_schedule() first.")
        return []

    with open(schedule_path, "r", encoding="utf-8") as f:
        games = json.load(f)

    h2h: dict[tuple, dict] = {}

    for g in games:
        home = g.get("home_team_id")
        away = g.get("away_team_id")
        winner = g.get("winner_nba_team_id")

        if home is None or away is None:
            continue

        # Enforce ordering
        if home < away:
            team_a, team_b = home, away
        else:
            team_a, team_b = away, home

        key = (team_a, team_b)

        if key not in h2h:
            h2h[key] = {
                "team_a_nba_id": team_a,
                "team_b_nba_id": team_b,
                "season": SEASON,
                "team_a_wins": 0,
                "team_b_wins": 0,
            }

        if winner is not None:
            if winner == team_a:
                h2h[key]["team_a_wins"] += 1
            elif winner == team_b:
                h2h[key]["team_b_wins"] += 1

    records = list(h2h.values())
    _save_json(records, "h2h.json")
    logger.info("Computed %d head-to-head records.", len(records))
    return records


def fetch_upcoming_games(days_ahead: int = 7) -> list[dict]:
    """
    Fetch upcoming/today's NBA games using ScoreboardV2.
    Queries each day from today to today + days_ahead.
    Only includes games that have NOT been completed yet (status 1 or 2).
    """
    logger.info("Fetching upcoming games for the next %d days...", days_ahead)
    _ensure_cache_dir()

    all_upcoming = []
    today = datetime.now()

    for day_offset in range(days_ahead):
        target_date = today + timedelta(days=day_offset)
        date_str = target_date.strftime("%Y-%m-%d")  # e.g. "2026-04-07"

        try:
            logger.info("Fetching scoreboard for %s (day %d/%d)...", date_str, day_offset + 1, days_ahead)
            sb = ScoreboardV2(game_date=date_str, league_id="00")
            time.sleep(DELAY)

            dfs = sb.get_data_frames()
            if not dfs or len(dfs) == 0:
                logger.info("No data for %s", date_str)
                continue

            # The first DataFrame is GameHeader
            game_header = dfs[0]
            if game_header.empty:
                logger.info("No games on %s", date_str)
                continue

            for _, row in game_header.iterrows():
                game_status = int(row.get("GAME_STATUS_ID", 0))

                # 1 = Not started (scheduled), 2 = In progress (live), 3 = Final
                if game_status == 3:
                    continue  # skip completed games, we already have those

                status_map = {1: "scheduled", 2: "live"}
                game_id = str(row.get("GAME_ID", ""))
                home_id = int(row.get("HOME_TEAM_ID", 0))
                visitor_id = int(row.get("VISITOR_TEAM_ID", 0))

                if not game_id or home_id == 0 or visitor_id == 0:
                    continue

                all_upcoming.append({
                    "nba_game_id": game_id,
                    "scheduled_date": date_str,
                    "season": SEASON,
                    "home_team_id": home_id,
                    "away_team_id": visitor_id,
                    "home_score": None,
                    "away_score": None,
                    "winner_nba_team_id": None,
                    "status": status_map.get(game_status, "scheduled"),
                })

            logger.info("Found %d upcoming/live games on %s",
                        sum(1 for g in all_upcoming if g["scheduled_date"] == date_str), date_str)

        except Exception as exc:
            logger.warning("Failed to fetch scoreboard for %s: %s", date_str, exc)
            continue

    _save_json(all_upcoming, "upcoming.json")
    logger.info("Total upcoming/live games fetched: %d", len(all_upcoming))
    return all_upcoming


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the full data fetch pipeline."""
    logger.info("=" * 60)
    logger.info("Starting NBA data fetch pipeline — Season %s", SEASON)
    logger.info("=" * 60)

    _ensure_cache_dir()

    teams = fetch_all_teams()
    logger.info("Teams: %d records", len(teams))

    players = fetch_player_stats()
    logger.info("Players: %d records", len(players))

    schedule = fetch_schedule()
    logger.info("Schedule: %d records", len(schedule))

    h2h = fetch_head_to_head()
    logger.info("Head-to-head: %d records", len(h2h))

    upcoming = fetch_upcoming_games()
    logger.info("Upcoming: %d records", len(upcoming))

    logger.info("=" * 60)
    logger.info("Data fetch pipeline completed successfully.")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
