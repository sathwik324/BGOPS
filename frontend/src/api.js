import axios from 'axios';

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  timeout: 15000,
});

export async function fetchRankings(season = '2025-26') {
  const { data } = await API.get('/rankings', { params: { season } });
  return data.rankings || [];
}

export async function fetchTopPlayers(season = '2025-26', limit = 20) {
  const { data } = await API.get('/top-players', { params: { season, limit } });
  return data.players || [];
}

export async function fetchMatches(season = '2025-26', limit = 20) {
  const { data } = await API.get('/matches', { params: { season, limit } });
  return data.matches || [];
}

export async function fetchTeams() {
  const { data } = await API.get('/teams');
  return data.teams || [];
}

export async function fetchPrediction(homeId, awayId, season = '2025-26') {
  const { data } = await API.get('/predict', {
    params: { home: homeId, away: awayId, season },
  });
  return data.prediction || {};
}

export default API;
