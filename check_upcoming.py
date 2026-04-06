from backend.db_connection import get_connection, release_connection
conn = get_connection()
c = conn.cursor()
c.execute("SELECT COUNT(match_id) FROM matches WHERE status='scheduled'")
cnt = c.fetchone()[0]
print(f"Total scheduled matches in DB: {cnt}")
print()
c.execute("SELECT m.scheduled_date, th.name AS home, ta.name AS away FROM matches m JOIN teams th ON th.team_id=m.home_team_id JOIN teams ta ON ta.team_id=m.away_team_id WHERE m.status='scheduled' ORDER BY m.scheduled_date LIMIT 15")
rows = c.fetchall()
for row in rows:
    print(f"  {row[0]}  {row[1]:20s} vs {row[2]}")
c.close()
release_connection(conn)
