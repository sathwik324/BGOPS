from nba_api.stats.endpoints import leaguedashteamstats

data = leaguedashteamstats.LeagueDashTeamStats()
df = data.get_data_frames()[0]

print(df.head())