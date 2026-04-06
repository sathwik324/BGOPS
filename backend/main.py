import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="BGOPS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "nba_predictions"),
    )


class PredictRequest(BaseModel):
    home_team_id: int
    away_team_id: int


# ---------- Routes ----------


@app.get("/")
def root():
    return {"status": "BGOPS API running"}


@app.get("/teams")
def get_teams():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT team_id, name, abbreviation FROM teams ORDER BY name"
        )
        rows = cursor.fetchall()
        return rows
    finally:
        cursor.close()
        conn.close()


@app.get("/rankings")
def get_rankings():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT name, wins, losses, win_ratio FROM teams ORDER BY win_ratio DESC"
        )
        rows = cursor.fetchall()
        # Convert Decimal to float for JSON serialisation
        for r in rows:
            if r.get("win_ratio") is not None:
                r["win_ratio"] = float(r["win_ratio"])
        return rows
    finally:
        cursor.close()
        conn.close()


@app.get("/top-players")
def get_top_players():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT p.full_name, ps.points_per_game, ps.player_score
            FROM player_stats ps
            JOIN players p ON ps.player_id = p.player_id
            WHERE ps.season = '2024-25'
            ORDER BY ps.player_score DESC
            LIMIT 30
            """
        )
        rows = cursor.fetchall()
        for r in rows:
            if r.get("points_per_game") is not None:
                r["points_per_game"] = float(r["points_per_game"])
            if r.get("player_score") is not None:
                r["player_score"] = float(r["player_score"])
        return rows
    finally:
        cursor.close()
        conn.close()


@app.get("/matches")
def get_matches():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT nba_game_id, scheduled_date, status
            FROM matches
            ORDER BY scheduled_date DESC
            LIMIT 20
            """
        )
        rows = cursor.fetchall()
        for r in rows:
            if r.get("scheduled_date") is not None:
                r["scheduled_date"] = str(r["scheduled_date"])
        return rows
    finally:
        cursor.close()
        conn.close()


@app.post("/predict")
def predict(req: PredictRequest):
    if req.home_team_id == req.away_team_id:
        raise HTTPException(status_code=400, detail="Teams must be different")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT wins, losses FROM teams WHERE team_id = %s",
            (req.home_team_id,),
        )
        home = cursor.fetchone()
        if not home:
            raise HTTPException(status_code=404, detail="Home team not found")

        cursor.execute(
            "SELECT wins, losses FROM teams WHERE team_id = %s",
            (req.away_team_id,),
        )
        away = cursor.fetchone()
        if not away:
            raise HTTPException(status_code=404, detail="Away team not found")

        home_wins = home["wins"]
        away_wins = away["wins"]
        total = home_wins + away_wins

        if total == 0:
            home_win_pct = 50.0
        else:
            home_win_pct = (home_wins / total) * 100

        # Clamp between 5 and 95
        home_win_pct = max(5.0, min(95.0, home_win_pct))
        away_win_pct = 100.0 - home_win_pct

        return {
            "home_team_id": req.home_team_id,
            "away_team_id": req.away_team_id,
            "home_win_pct": round(home_win_pct, 2),
            "away_win_pct": round(away_win_pct, 2),
        }
    finally:
        cursor.close()
        conn.close()
