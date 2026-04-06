"""
NBA Game Outcome Prediction System — FastAPI Backend
Wraps existing queries.py functions as REST endpoints.
"""

import sys
import os
from decimal import Decimal
from datetime import date, datetime

# Ensure project root is on sys.path so `backend.queries` resolves
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.queries import (
    get_team_rankings,
    get_top_players,
    get_upcoming_matches,
    predict_match,
    get_teams_lookup,
)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(title="NBA Prediction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SEASON = "2025-26"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _serialize(obj):
    """Convert Decimal / date objects to JSON-safe types."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return obj


def _clean(rows):
    """Recursively make every value in a list[dict] JSON-serializable."""
    if isinstance(rows, list):
        return [{k: _serialize(v) for k, v in row.items()} for row in rows]
    if isinstance(rows, dict):
        return {k: _serialize(v) for k, v in rows.items()}
    return rows


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"status": "ok", "message": "NBA Prediction API is running"}


@app.get("/rankings")
def rankings(season: str = Query(default=SEASON)):
    """Return all teams ranked by win ratio + custom team_score."""
    try:
        data = get_team_rankings(season)
        return {"season": season, "rankings": _clean(data)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/top-players")
def top_players(season: str = Query(default=SEASON), limit: int = Query(default=30)):
    """Return top N players by player_score."""
    try:
        data = get_top_players(season, limit)
        return {"season": season, "players": _clean(data)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/matches")
def matches(season: str = Query(default=SEASON), limit: int = Query(default=20)):
    """Return upcoming / recent matches."""
    try:
        data = get_upcoming_matches(season, limit)
        return {"season": season, "matches": _clean(data)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/teams")
def teams():
    """Return team lookup list (id, name, abbreviation)."""
    try:
        data = get_teams_lookup()
        return {"teams": _clean(data)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predict")
def predict(
    home: int = Query(..., description="Home team_id"),
    away: int = Query(..., description="Away team_id"),
    season: str = Query(default=SEASON),
):
    """
    Predict win probability for a matchup.
    GET /predict?home=1&away=2
    """
    if home == away:
        raise HTTPException(status_code=400, detail="home and away must be different teams")
    try:
        result = predict_match(home, away, season)
        if not result:
            raise HTTPException(status_code=404, detail="No prediction data available")
        return {"season": season, "prediction": _clean(result)}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
