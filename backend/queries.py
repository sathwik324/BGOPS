"""
NBA Game Outcome Prediction System — Backend: Query Functions
All queries use parameterized statements and the connection pool.
Returns list[dict]. Logs and re-raises errors as RuntimeError.
"""

import logging
from backend.db_connection import get_connection, release_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def _rows_to_dicts(cursor) -> list[dict]:
    """Convert cursor results to a list of dicts using column names."""
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]


def _fetch_proc_results(cursor) -> list[dict]:
    """
    Fetch the result set from a stored procedure call.
    MySQL stored procedures return results as stored_results().
    """
    results = []
    for result in cursor.stored_results():
        columns = [desc[0] for desc in result.description] if result.description else []
        for row in result.fetchall():
            results.append(dict(zip(columns, row)))
    return results


# ---------------------------------------------------------------------------
# Query functions
# ---------------------------------------------------------------------------

def get_top_players(season: str, limit: int = 30) -> list[dict]:
    """
    Retrieve top players for a given season, ranked by player_score.
    Calls the get_top_players stored procedure.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.callproc("get_top_players", [season, limit])
        results = _fetch_proc_results(cursor)
        cursor.close()

        logger.info("get_top_players: returned %d players for season %s", len(results), season)
        return results if results else []

    except Exception as e:
        logger.error("get_top_players failed: %s", e)
        raise RuntimeError(f"Failed to get top players: {e}") from e
    finally:
        if conn:
            release_connection(conn)


def get_team_rankings(season: str) -> list[dict]:
    """
    Retrieve team rankings for a given season.
    Calls the get_team_rankings stored procedure.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.callproc("get_team_rankings", [season])
        results = _fetch_proc_results(cursor)
        cursor.close()

        logger.info("get_team_rankings: returned %d teams for season %s", len(results), season)
        return results if results else []

    except Exception as e:
        logger.error("get_team_rankings failed: %s", e)
        raise RuntimeError(f"Failed to get team rankings: {e}") from e
    finally:
        if conn:
            release_connection(conn)


def predict_match(home_id: int, away_id: int, season: str) -> dict:
    """
    Predict the outcome of a match between two teams.
    Calls the predict_match stored procedure.
    Returns a single dict with prediction details.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.callproc("predict_match", [home_id, away_id, season])
        results = _fetch_proc_results(cursor)
        cursor.close()

        if results:
            logger.info(
                "predict_match: home=%d vs away=%d → home_pct=%.2f%%",
                home_id, away_id, float(results[0].get("home_win_pct", 0)),
            )
            return results[0]

        logger.warning("predict_match: no results for home=%d, away=%d", home_id, away_id)
        return {}

    except Exception as e:
        logger.error("predict_match failed: %s", e)
        raise RuntimeError(f"Failed to predict match: {e}") from e
    finally:
        if conn:
            release_connection(conn)


def get_teams_lookup() -> list[dict]:
    """
    Retrieve a lookup list of all teams (team_id, name, abbreviation).
    Ordered alphabetically by name.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT team_id, name, abbreviation FROM teams ORDER BY name ASC"
        )
        results = _rows_to_dicts(cursor)
        cursor.close()

        logger.info("get_teams_lookup: returned %d teams", len(results))
        return results if results else []

    except Exception as e:
        logger.error("get_teams_lookup failed: %s", e)
        raise RuntimeError(f"Failed to get teams lookup: {e}") from e
    finally:
        if conn:
            release_connection(conn)


def get_upcoming_matches(season: str, limit: int = 10) -> list[dict]:
    """
    Retrieve upcoming scheduled matches with team names.
    Ordered by scheduled date ascending.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT
                m.match_id,
                m.nba_game_id,
                m.scheduled_date,
                m.status,
                m.season,
                th.name        AS home_team,
                th.abbreviation AS home_abbr,
                ta.name        AS away_team,
                ta.abbreviation AS away_abbr,
                m.home_team_id,
                m.away_team_id
            FROM matches m
            INNER JOIN teams th ON th.team_id = m.home_team_id
            INNER JOIN teams ta ON ta.team_id = m.away_team_id
            WHERE m.status IN ('scheduled', 'live')
              AND m.season = %s
            ORDER BY m.scheduled_date ASC
            LIMIT %s
        """
        cursor.execute(sql, (season, limit))
        results = _rows_to_dicts(cursor)
        cursor.close()

        logger.info("get_upcoming_matches: returned %d matches for season %s", len(results), season)
        return results if results else []

    except Exception as e:
        logger.error("get_upcoming_matches failed: %s", e)
        raise RuntimeError(f"Failed to get upcoming matches: {e}") from e
    finally:
        if conn:
            release_connection(conn)
