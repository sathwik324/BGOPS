from backend.queries import get_upcoming_matches, predict_match, get_team_rankings

def main():
    print("\n🏀 NBA Game Outcome Prediction System 🏀\n")
    
    # 1. Show Top 5 Teams by the Custom Score
    print("--- Top 5 Teams by Power Score ---")
    rankings = get_team_rankings("2024-25")
    for i, team in enumerate(rankings[:5]):
        print(f"{i+1}. {team['name']} ({team['wins']}W - {team['losses']}L) | System Score: {float(team['team_score']):.2f}")
        
    # 2. Predict Upcoming Matches
    print("\n--- Upcoming Match Predictions ---")
    matches = get_upcoming_matches("2024-25", limit=5)
    
    if not matches:
        print("No upcoming matches found in the schedule.")
        
    for match in matches:
        home_team = match['home_team']
        away_team = match['away_team']
        date = match['scheduled_date']
        
        print(f"\nMatch: {away_team} @ {home_team} (Date: {date})")
        
        # Calculate the prediction using your SQL stored procedures
        prediction = predict_match(match['home_team_id'], match['away_team_id'], "2024-25")
        
        if prediction:
            home_pct = float(prediction['home_win_pct'])
            away_pct = float(prediction['away_win_pct'])
            
            if home_pct > away_pct:
                favored = f"🏆 {home_team} ({home_pct}%)"
                underdog = f"{away_team} ({away_pct}%)"
            else:
                favored = f"🏆 {away_team} ({away_pct}%)"
                underdog = f"{home_team} ({home_pct}%)"
                
            print(f"Prediction: {favored} vs {underdog}")
            print(f"H2H Advantage: {float(prediction['h2h_win_pct'])*100:.1f}% for {home_team}")

if __name__ == "__main__":
    main()
