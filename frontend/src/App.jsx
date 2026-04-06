import { useState, useEffect } from 'react';
import './App.css';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import MatchCard from './components/MatchCard';
import ExpertPanel from './components/ExpertPanel';
import Leaderboard from './components/Leaderboard';
import TopPlayers from './components/TopPlayers';
import PredictionEngine from './components/PredictionEngine';
import {
  fetchRankings, fetchMatches, fetchTeams, fetchTopPlayers, fetchPrediction,
} from './api';

export default function App() {
  const [rankings, setRankings] = useState([]);
  const [matches, setMatches] = useState([]);
  const [teams, setTeams] = useState([]);
  const [players, setPlayers] = useState([]);
  const [predictions, setPredictions] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const [r, m, t, p] = await Promise.all([
          fetchRankings(), fetchMatches(), fetchTeams(), fetchTopPlayers('2025-26', 10),
        ]);
        setRankings(r); setMatches(m); setTeams(t); setPlayers(p);
      } catch (err) {
        console.error(err);
        setError('Could not connect to the API. Make sure the FastAPI server is running on port 8000.');
      } finally { setLoading(false); }
    })();
  }, []);

  const handlePredict = async (match) => {
    try {
      const result = await fetchPrediction(match.home_team_id, match.away_team_id);
      setPredictions(prev => ({ ...prev, [match.match_id]: result }));
    } catch (err) { console.error(err); }
  };

  // Helper: format ISO date string to a friendly label
  const formatMatchDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr; // already a label string
      const now = new Date();
      const tomorrow = new Date(now);
      tomorrow.setDate(now.getDate() + 1);
      
      const isToday = d.toDateString() === now.toDateString();
      const isTomorrow = d.toDateString() === tomorrow.toDateString();
      
      if (isToday) return 'Today';
      if (isTomorrow) return 'Tomorrow';
      return d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    } catch { return dateStr; }
  };

  // Sanitize abbreviation (fix 'nan' from DB)
  const cleanAbbr = (abbr, name) =>
    (!abbr || String(abbr).toLowerCase() === 'nan') ? name.substring(0, 3).toUpperCase() : abbr;

  const matchList = matches.map(m => ({
    ...m,
    home_abbr: cleanAbbr(m.home_abbr, m.home_team || ''),
    away_abbr: cleanAbbr(m.away_abbr, m.away_team || ''),
    scheduled_date: formatMatchDate(m.scheduled_date),
  }));

  const featuredMatch = matchList[0];
  const otherMatches = matchList.slice(1, 6);

  return (
    <div style={{ background: 'var(--bg-base)', minHeight: '100vh' }}>
      <Navbar />

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="w-16 h-16 border-4 rounded-full animate-spin mx-auto mb-6"
                 style={{ borderColor: 'var(--border)', borderTopColor: 'var(--accent)' }} />
            <p className="text-lg font-semibold" style={{ color: 'var(--text-secondary)' }}>Loading NBA data...</p>
          </div>
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="flex items-center justify-center min-h-screen">
          <div className="card text-center" style={{ padding: '60px', borderRadius: '24px', maxWidth: '480px' }}>
            <div className="text-5xl mb-6">⚠️</div>
            <h2 className="text-xl font-bold mb-3">Connection Failed</h2>
            <p className="text-sm mb-6" style={{ color: 'var(--text-secondary)' }}>{error}</p>
          </div>
        </div>
      )}

      {!loading && !error && (
        <>
          {/* ═══ HERO ═══ */}
          <HeroSection topTeams={rankings} />

          <div className="section-divider" />

          {/* ═══ LIVE & UPCOMING ═══ */}
          <section id="games" style={{ paddingTop: '100px', paddingBottom: '100px' }}>
            <div className="page-container">
              {/* Section Header */}
              <div className="flex items-center justify-between" style={{ marginBottom: '48px' }}>
                <div className="flex items-center gap-4">
                  <div className="w-1.5 h-10 rounded-full" style={{ background: 'var(--accent)' }} />
                  <div>
                    <h2 className="text-2xl font-black uppercase tracking-tight"
                        style={{ fontFamily: 'var(--font-heading)' }}>
                      Live & Upcoming
                    </h2>
                    <p className="text-sm mt-2" style={{ color: 'var(--text-muted)' }}>
                      Tonight&#39;s matchups and prediction opportunities
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button className="w-10 h-10 rounded-xl flex items-center justify-center cursor-pointer"
                          style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}>←</button>
                  <button className="w-10 h-10 rounded-xl flex items-center justify-center cursor-pointer"
                          style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}>→</button>
                </div>
              </div>

              {/* Featured + Expert sidebar */}
              <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-10">
                <div className="flex flex-col gap-8">
                  {featuredMatch && (
                    <MatchCard match={featuredMatch}
                               prediction={predictions[featuredMatch.match_id]}
                               onPredict={handlePredict}
                               featured />
                  )}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    {otherMatches.map(m => (
                      <MatchCard key={m.match_id} match={m}
                                 prediction={predictions[m.match_id]}
                                 onPredict={handlePredict} />
                    ))}
                  </div>
                </div>
                <ExpertPanel rankings={rankings} />
              </div>
            </div>
          </section>

          <div className="section-divider" />

          {/* ═══ PREDICTION ENGINE ═══ */}
          <PredictionEngine teams={teams} />

          <div className="section-divider" />

          {/* ═══ LEADERBOARD ═══ */}
          <Leaderboard rankings={rankings} />

          <div className="section-divider" />

          {/* ═══ MVP TRACKER ═══ */}
          <TopPlayers players={players} />

          {/* ═══ FOOTER ═══ */}
          <footer style={{ padding: '80px 0', borderTop: '1px solid var(--border)' }}>
            <div className="page-container flex flex-col md:flex-row items-center justify-between gap-8">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl flex items-center justify-center"
                     style={{ background: 'linear-gradient(135deg, var(--accent), var(--accent-dim))' }}>
                  <span className="text-lg">🏀</span>
                </div>
                <span className="text-3xl font-black tracking-tight"
                      style={{ fontFamily: 'var(--font-heading)', color: 'var(--accent)' }}>
                  BGOPS
                </span>
              </div>
              <p className="text-xs tracking-wide" style={{ color: 'var(--text-dim)' }}>
                Data powered by nba_api · Built with FastAPI + React · 2025-26 Season
              </p>
              <div className="flex items-center gap-6">
                {['Twitter', 'Discord', 'GitHub'].map(s => (
                  <span key={s} className="text-xs font-medium cursor-pointer" style={{ color: 'var(--text-muted)' }}>{s}</span>
                ))}
              </div>
            </div>
          </footer>
        </>
      )}
    </div>
  );
}
