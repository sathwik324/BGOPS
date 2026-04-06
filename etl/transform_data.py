"""
NBA Game Outcome Prediction System — ETL: Transform Data
Reads raw JSON from ./data_cache/, cleans and validates, writes clean CSVs.
"""

import os
import json
import logging
import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CACHE_DIR = "./data_cache"
CLEAN_DIR = os.path.join(CACHE_DIR, "clean")

VALID_CONFERENCES = {"East", "West"}
VALID_STATUSES = {"scheduled", "live", "completed"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def _load_json(filename: str) -> list[dict]:
    """Load a JSON file from the cache directory."""
    filepath = os.path.join(CACHE_DIR, filename)
    if not os.path.exists(filepath):
        logger.error("File not found: %s", filepath)
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.info("Loaded %d records from %s", len(data), filepath)
    return data


def _save_csv(df: pd.DataFrame, filename: str) -> None:
    """Save a DataFrame to CSV in the clean directory."""
    os.makedirs(CLEAN_DIR, exist_ok=True)
    filepath = os.path.join(CLEAN_DIR, filename)
    df.to_csv(filepath, index=False, encoding="utf-8")
    logger.info("Saved %d rows to %s", len(df), filepath)


# ---------------------------------------------------------------------------
# Transform functions
# ---------------------------------------------------------------------------

def transform_teams() -> pd.DataFrame:
    """
    Clean teams data:
    - Drop duplicates on nba_team_id
    - Validate conference values
    - Ensure non-negative wins/losses
    - Fill NaN values
    """
    raw = _load_json("teams.json")
    if not raw:
        return pd.DataFrame()

    df = pd.DataFrame(raw)
    before_count = len(df)

    # Drop duplicates
    df = df.drop_duplicates(subset=["nba_team_id"], keep="first")

    # Fill NaN strings
    for col in ["name", "abbreviation", "city", "division"]:
        df[col] = df[col].fillna("Unknown")

    # Validate conference
    df["conference"] = df["conference"].apply(
        lambda c: c if c in VALID_CONFERENCES else "East"
    )

    # Ensure non-negative integers
    for col in ["wins", "losses", "last_10_wins", "last_10_losses"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        df[col] = df[col].clip(lower=0)

    # Ensure nba_team_id is integer
    df["nba_team_id"] = df["nba_team_id"].astype(int)

    logger.info("Teams: %d → %d rows after cleaning", before_count, len(df))
    _save_csv(df, "teams.csv")
    return df


def transform_players(teams_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean player stats data:
    - Merge team_id via nba_team_id join
    - Clip stats >= 0
    - Round to 2 decimal places
    - Set is_active = True
    """
    raw = _load_json("player_stats.json")
    if not raw:
        return pd.DataFrame()

    df = pd.DataFrame(raw)
    before_count = len(df)

    # Merge team_id from teams
    team_lookup = teams_df[["nba_team_id"]].copy()
    team_lookup = team_lookup.reset_index(drop=True)
    df = df.merge(team_lookup, on="nba_team_id", how="left")

    # Fill missing names
    df["full_name"] = df["full_name"].fillna("Unknown Player")
    df["position"] = df["position"].fillna("")

    # Clip numeric stat columns >= 0 and round to 2dp
    stat_cols = [
        "points_per_game", "assists_per_game", "rebounds_per_game",
        "steals_per_game", "blocks_per_game", "minutes_per_game",
    ]
    for col in stat_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        df[col] = df[col].clip(lower=0).round(2)

    # Ensure integer columns
    df["games_played"] = pd.to_numeric(df["games_played"], errors="coerce").fillna(0).astype(int)
    df["nba_player_id"] = df["nba_player_id"].astype(int)
    df["nba_team_id"] = df["nba_team_id"].astype(int)

    # Set is_active
    df["is_active"] = True

    # Drop duplicates on (nba_player_id, season)
    df = df.drop_duplicates(subset=["nba_player_id", "season"], keep="first")

    logger.info("Players: %d → %d rows after cleaning", before_count, len(df))
    _save_csv(df, "players.csv")
    return df


def transform_schedule() -> pd.DataFrame:
    """
    Clean schedule data:
    - Validate dates as YYYY-MM-DD
    - Validate status values
    - Set winner to NULL if status != completed
    """
    raw = _load_json("schedule.json")
    if not raw:
        return pd.DataFrame()

    df = pd.DataFrame(raw)
    before_count = len(df)

    # Validate and format dates
    df["scheduled_date"] = pd.to_datetime(df["scheduled_date"], errors="coerce")
    df = df.dropna(subset=["scheduled_date"])
    df["scheduled_date"] = df["scheduled_date"].dt.strftime("%Y-%m-%d")

    # Validate status
    df["status"] = df["status"].apply(
        lambda s: s if s in VALID_STATUSES else "scheduled"
    )

    # NULL winner if not completed
    df.loc[df["status"] != "completed", "winner_nba_team_id"] = None

    # Drop games missing both teams
    df = df.dropna(subset=["home_team_id", "away_team_id"])

    # Ensure integer types where possible
    for col in ["home_team_id", "away_team_id"]:
        df[col] = df[col].astype(int)

    for col in ["home_score", "away_score"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        # Keep NaN as-is (will become NULL in DB)

    df["winner_nba_team_id"] = pd.to_numeric(df["winner_nba_team_id"], errors="coerce")

    # Drop duplicate game IDs
    df = df.drop_duplicates(subset=["nba_game_id"], keep="first")

    logger.info("Schedule: %d → %d rows after cleaning", before_count, len(df))
    _save_csv(df, "schedule.csv")
    return df


def transform_h2h() -> pd.DataFrame:
    """
    Clean head-to-head records:
    - Enforce team_a < team_b (swap + recalculate if violated)
    - Drop duplicates
    """
    raw = _load_json("h2h.json")
    if not raw:
        return pd.DataFrame()

    df = pd.DataFrame(raw)
    before_count = len(df)

    # Ensure integer types
    df["team_a_nba_id"] = df["team_a_nba_id"].astype(int)
    df["team_b_nba_id"] = df["team_b_nba_id"].astype(int)
    df["team_a_wins"] = pd.to_numeric(df["team_a_wins"], errors="coerce").fillna(0).astype(int)
    df["team_b_wins"] = pd.to_numeric(df["team_b_wins"], errors="coerce").fillna(0).astype(int)

    # Enforce team_a < team_b — swap if violated
    swap_mask = df["team_a_nba_id"] > df["team_b_nba_id"]
    if swap_mask.any():
        logger.info("Swapping %d rows to enforce team_a < team_b", swap_mask.sum())
        # Swap team IDs
        df.loc[swap_mask, ["team_a_nba_id", "team_b_nba_id"]] = (
            df.loc[swap_mask, ["team_b_nba_id", "team_a_nba_id"]].values
        )
        # Swap wins accordingly
        df.loc[swap_mask, ["team_a_wins", "team_b_wins"]] = (
            df.loc[swap_mask, ["team_b_wins", "team_a_wins"]].values
        )

    # Drop duplicates
    df = df.drop_duplicates(subset=["team_a_nba_id", "team_b_nba_id", "season"], keep="first")

    logger.info("H2H: %d → %d rows after cleaning", before_count, len(df))
    _save_csv(df, "h2h.csv")
    return df


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the full data transformation pipeline."""
    logger.info("=" * 60)
    logger.info("Starting data transformation pipeline")
    logger.info("=" * 60)

    teams_df = transform_teams()
    transform_players(teams_df)
    transform_schedule()
    transform_h2h()

    logger.info("=" * 60)
    logger.info("Data transformation pipeline completed successfully.")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
