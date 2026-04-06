"""
NBA Game Outcome Prediction System — ETL: Load Data
Reads clean CSVs from ./data_cache/clean/, upserts into MySQL.
DB credentials from environment variables.
"""

import os
import time
import logging
import pandas as pd
import numpy as np
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CLEAN_DIR = "./data_cache/clean"
SEASON = "2025-26"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def _get_db_config() -> dict:
    """Build MySQL connection config from environment variables."""
    return {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", 3306)),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "database": os.environ.get("DB_NAME", "nba_predictions"),
    }


def _get_connection():
    """Create a new MySQL connection."""
    config = _get_db_config()
    conn = mysql.connector.connect(**config)
    conn.autocommit = False
    return conn


def _read_csv(filename: str) -> pd.DataFrame:
    """Read a CSV from the clean directory."""
    filepath = os.path.join(CLEAN_DIR, filename)
    if not os.path.exists(filepath):
        logger.error("Clean file not found: %s", filepath)
        return pd.DataFrame()
    df = pd.read_csv(filepath, encoding="utf-8")
    logger.info("Read %d rows from %s", len(df), filepath)
    return df


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def _build_team_lookup(cursor) -> dict[int, int]:
    """
    Build a mapping of nba_team_id → team_id from the database.
    """
    cursor.execute("SELECT team_id, nba_team_id FROM teams")
    rows = cursor.fetchall()
    lookup = {int(row[1]): int(row[0]) for row in rows}
    logger.info("Team lookup: %d entries", len(lookup))
    return lookup


def _build_player_lookup(cursor) -> dict[int, int]:
    """
    Build a mapping of nba_player_id → player_id from the database.
    """
    cursor.execute("SELECT player_id, nba_player_id FROM players")
    rows = cursor.fetchall()
    lookup = {int(row[1]): int(row[0]) for row in rows}
    logger.info("Player lookup: %d entries", len(lookup))
    return lookup


# ---------------------------------------------------------------------------
# Load functions
# ---------------------------------------------------------------------------

def load_teams(conn) -> int:
    """
    Upsert teams into the teams table.
    Uses INSERT ... ON DUPLICATE KEY UPDATE.
    """
    df = _read_csv("teams.csv")
    if df.empty:
        return 0

    cursor = conn.cursor()
    sql = """
        INSERT INTO teams (nba_team_id, name, abbreviation, city, conference,
                           division, wins, losses, last_10_wins, last_10_losses)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name           = VALUES(name),
            abbreviation   = VALUES(abbreviation),
            city           = VALUES(city),
            conference     = VALUES(conference),
            division       = VALUES(division),
            wins           = VALUES(wins),
            losses         = VALUES(losses),
            last_10_wins   = VALUES(last_10_wins),
            last_10_losses = VALUES(last_10_losses)
    """

    rows = []
    for _, r in df.iterrows():
        rows.append((
            int(r["nba_team_id"]), str(r["name"]), str(r["abbreviation"]),
            str(r["city"]), str(r["conference"]), str(r["division"]),
            int(r["wins"]), int(r["losses"]),
            int(r["last_10_wins"]), int(r["last_10_losses"]),
        ))

    cursor.executemany(sql, rows)
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    logger.info("Teams: %d rows affected", affected)
    return affected


def load_players(conn) -> int:
    """
    Upsert players into the players table.
    Resolves nba_team_id → team_id via lookup query.
    """
    df = _read_csv("players.csv")
    if df.empty:
        return 0

    cursor = conn.cursor()
    team_lookup = _build_team_lookup(cursor)

    sql = """
        INSERT INTO players (nba_player_id, team_id, full_name, position, is_active)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            team_id   = VALUES(team_id),
            full_name = VALUES(full_name),
            position  = VALUES(position),
            is_active = VALUES(is_active)
    """

    rows = []
    skipped = 0
    for _, r in df.iterrows():
        nba_team_id = int(r["nba_team_id"])
        team_id = team_lookup.get(nba_team_id)
        if team_id is None:
            skipped += 1
            continue

        rows.append((
            int(r["nba_player_id"]),
            team_id,
            str(r["full_name"]),
            str(r.get("position", "")),
            bool(r.get("is_active", True)),
        ))

    if skipped:
        logger.warning("Skipped %d players with unmapped team IDs", skipped)

    cursor.executemany(sql, rows)
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    logger.info("Players: %d rows affected", affected)
    return affected


def load_player_stats(conn) -> int:
    """
    Upsert player stats into the player_stats table.
    Resolves nba_player_id → player_id via lookup query.
    """
    df = _read_csv("players.csv")  # Player stats are in players.csv
    if df.empty:
        return 0

    cursor = conn.cursor()
    player_lookup = _build_player_lookup(cursor)

    sql = """
        INSERT INTO player_stats (player_id, season, games_played,
                                  points_per_game, assists_per_game,
                                  rebounds_per_game, steals_per_game,
                                  blocks_per_game, minutes_per_game)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            games_played      = VALUES(games_played),
            points_per_game   = VALUES(points_per_game),
            assists_per_game  = VALUES(assists_per_game),
            rebounds_per_game = VALUES(rebounds_per_game),
            steals_per_game   = VALUES(steals_per_game),
            blocks_per_game   = VALUES(blocks_per_game),
            minutes_per_game  = VALUES(minutes_per_game)
    """

    rows = []
    skipped = 0
    for _, r in df.iterrows():
        nba_player_id = int(r["nba_player_id"])
        player_id = player_lookup.get(nba_player_id)
        if player_id is None:
            skipped += 1
            continue

        rows.append((
            player_id,
            str(r["season"]),
            int(r["games_played"]),
            float(r["points_per_game"]),
            float(r["assists_per_game"]),
            float(r["rebounds_per_game"]),
            float(r["steals_per_game"]),
            float(r["blocks_per_game"]),
            float(r["minutes_per_game"]),
        ))

    if skipped:
        logger.warning("Skipped %d player_stats with unmapped player IDs", skipped)

    cursor.executemany(sql, rows)
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    logger.info("Player stats: %d rows affected", affected)
    return affected


def load_schedule(conn) -> int:
    """
    Upsert match schedule into the matches table.
    Resolves nba_team_id → team_id for home, away, and winner.
    """
    df = _read_csv("schedule.csv")
    if df.empty:
        return 0

    cursor = conn.cursor()
    team_lookup = _build_team_lookup(cursor)

    sql = """
        INSERT INTO matches (nba_game_id, home_team_id, away_team_id,
                             scheduled_date, status, home_score, away_score,
                             winner_team_id, season)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            home_team_id   = VALUES(home_team_id),
            away_team_id   = VALUES(away_team_id),
            scheduled_date = VALUES(scheduled_date),
            status         = VALUES(status),
            home_score     = VALUES(home_score),
            away_score     = VALUES(away_score),
            winner_team_id = VALUES(winner_team_id)
    """

    rows = []
    skipped = 0
    for _, r in df.iterrows():
        home_nba = int(r["home_team_id"])
        away_nba = int(r["away_team_id"])
        home_id = team_lookup.get(home_nba)
        away_id = team_lookup.get(away_nba)

        if home_id is None or away_id is None:
            skipped += 1
            continue

        # Resolve winner
        winner_id = None
        winner_nba = r.get("winner_nba_team_id")
        if pd.notna(winner_nba):
            winner_id = team_lookup.get(int(winner_nba))

        # Handle nullable scores
        home_score = None if pd.isna(r.get("home_score")) else int(r["home_score"])
        away_score = None if pd.isna(r.get("away_score")) else int(r["away_score"])

        rows.append((
            str(r["nba_game_id"]),
            home_id,
            away_id,
            str(r["scheduled_date"]),
            str(r["status"]),
            home_score,
            away_score,
            winner_id,
            str(r["season"]),
        ))

    if skipped:
        logger.warning("Skipped %d games with unmapped team IDs", skipped)

    cursor.executemany(sql, rows)
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    logger.info("Schedule: %d rows affected", affected)
    return affected


def load_h2h(conn) -> int:
    """
    Upsert head-to-head records.
    Resolves nba_team_id → team_id and ensures team_a < team_b ordering.
    """
    df = _read_csv("h2h.csv")
    if df.empty:
        return 0

    cursor = conn.cursor()
    team_lookup = _build_team_lookup(cursor)

    sql = """
        INSERT INTO head_to_head (team_a_id, team_b_id, season,
                                  team_a_wins, team_b_wins)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            team_a_wins = VALUES(team_a_wins),
            team_b_wins = VALUES(team_b_wins)
    """

    rows = []
    skipped = 0
    for _, r in df.iterrows():
        a_nba = int(r["team_a_nba_id"])
        b_nba = int(r["team_b_nba_id"])
        a_id = team_lookup.get(a_nba)
        b_id = team_lookup.get(b_nba)

        if a_id is None or b_id is None:
            skipped += 1
            continue

        # Ensure ordering a_id < b_id
        a_wins = int(r["team_a_wins"])
        b_wins = int(r["team_b_wins"])

        if a_id > b_id:
            a_id, b_id = b_id, a_id
            a_wins, b_wins = b_wins, a_wins

        rows.append((a_id, b_id, str(r["season"]), a_wins, b_wins))

    if skipped:
        logger.warning("Skipped %d H2H records with unmapped team IDs", skipped)

    cursor.executemany(sql, rows)
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    logger.info("H2H: %d rows affected", affected)
    return affected


def load_upcoming(conn) -> int:
    """
    Load upcoming/scheduled games from upcoming.json into the matches table.
    First clears old 'scheduled' entries, then inserts fresh ones.
    Uses INSERT IGNORE to skip any that already exist as completed games.
    """
    import json
    upcoming_path = os.path.join("./data_cache", "upcoming.json")
    if not os.path.exists(upcoming_path):
        logger.warning("upcoming.json not found — skipping upcoming games load")
        return 0

    with open(upcoming_path, "r", encoding="utf-8") as f:
        upcoming = json.load(f)

    if not upcoming:
        logger.info("No upcoming games to load")
        return 0

    cursor = conn.cursor()
    team_lookup = _build_team_lookup(cursor)

    # First: remove old scheduled games so we get fresh data each run
    cursor.execute("DELETE FROM matches WHERE status = 'scheduled'")
    deleted = cursor.rowcount
    logger.info("Cleared %d old scheduled games from matches table", deleted)

    sql = """
        INSERT IGNORE INTO matches
            (nba_game_id, home_team_id, away_team_id, scheduled_date,
             status, home_score, away_score, winner_team_id, season)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    rows = []
    skipped = 0
    for g in upcoming:
        home_nba = int(g["home_team_id"])
        away_nba = int(g["away_team_id"])
        home_id = team_lookup.get(home_nba)
        away_id = team_lookup.get(away_nba)

        if home_id is None or away_id is None:
            skipped += 1
            continue

        rows.append((
            str(g["nba_game_id"]),
            home_id,
            away_id,
            str(g["scheduled_date"]),
            str(g["status"]),
            None,   # home_score
            None,   # away_score
            None,   # winner_team_id
            str(g["season"]),
        ))

    if skipped:
        logger.warning("Skipped %d upcoming games with unmapped team IDs", skipped)

    if rows:
        cursor.executemany(sql, rows)
        conn.commit()
        affected = cursor.rowcount
    else:
        conn.commit()
        affected = 0

    cursor.close()
    logger.info("Upcoming: inserted %d scheduled games", affected)
    return affected


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the full data load pipeline."""
    logger.info("=" * 60)
    logger.info("Starting data load pipeline")
    logger.info("=" * 60)

    start = time.time()
    conn = _get_connection()

    try:
        logger.info("--- Loading teams ---")
        load_teams(conn)

        logger.info("--- Loading players ---")
        load_players(conn)

        logger.info("--- Loading player stats ---")
        load_player_stats(conn)

        logger.info("--- Loading schedule ---")
        load_schedule(conn)

        logger.info("--- Loading head-to-head ---")
        load_h2h(conn)

        logger.info("--- Loading upcoming games ---")
        load_upcoming(conn)

        # Refresh player scores via stored procedure
        logger.info("--- Refreshing player scores ---")
        cursor = conn.cursor()
        cursor.callproc("refresh_player_scores", [SEASON])
        conn.commit()
        cursor.close()
        logger.info("Player scores refreshed for season %s", SEASON)

    except Exception as e:
        logger.error("Load pipeline failed: %s", e)
        conn.rollback()
        raise
    finally:
        conn.close()

    elapsed = time.time() - start
    logger.info("=" * 60)
    logger.info("Data load pipeline completed in %.2f seconds.", elapsed)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

