import { useState } from 'react';
import { fetchPrediction } from '../api';
import PredictionBar from './PredictionBar';

export default function PredictionEngine({ teams = [] }) {
  const [homeId, setHomeId] = useState('');
  const [awayId, setAwayId] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePredict = async () => {
    if (!homeId || !awayId) { setError('Select both teams'); return; }
    if (homeId === awayId) { setError('Pick two different teams'); return; }
    setError('');
    setLoading(true);
    setPrediction(null);
    try {
      const result = await fetchPrediction(Number(homeId), Number(awayId));
      setPrediction(result);
    } catch {
      setError('Prediction failed. Try again.');
    } finally {
      setLoading(false);
    }
  };

  const homeName = teams.find(t => String(t.team_id) === homeId);
  const awayName = teams.find(t => String(t.team_id) === awayId);

  return (
    <section id="predictions" style={{ paddingTop: '100px', paddingBottom: '100px' }}>
      <div className="page-container">
        {/* Header */}
        <div className="flex items-center gap-4" style={{ marginBottom: '48px' }}>
          <div className="w-1.5 h-10 rounded-full" style={{ background: 'var(--accent)' }} />
          <div>
            <h2 className="text-2xl font-black uppercase tracking-tight" style={{ fontFamily: 'var(--font-heading)' }}>
              Prediction Engine
            </h2>
            <p className="text-sm mt-2" style={{ color: 'var(--text-muted)' }}>
              Select two teams and run the AI-powered prediction model
            </p>
          </div>
        </div>

        <div className="card" style={{ padding: '80px 48px', borderRadius: '24px' }}>
          <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-8 items-end" style={{ marginBottom: '36px' }}>
            <div>
              <label className="block text-[10px] font-bold uppercase tracking-[2px] mb-3" style={{ color: 'var(--text-muted)' }}>
                🏠 Home Team
              </label>
              <select value={homeId} onChange={e => setHomeId(e.target.value)}
                      className="select-dark w-full px-5 py-4 rounded-xl text-sm font-medium">
                <option value="">Select home team...</option>
                {teams.map(t => <option key={t.team_id} value={t.team_id}>{t.name} ({t.abbreviation})</option>)}
              </select>
            </div>
            <div className="hidden md:flex items-center justify-center pb-1">
              <div className="w-14 h-14 rounded-full flex items-center justify-center text-lg font-black"
                   style={{ background: 'var(--bg-elevated)', color: 'var(--text-dim)', fontFamily: 'var(--font-heading)', border: '1px solid var(--border)' }}>
                VS
              </div>
            </div>
            <div>
              <label className="block text-[10px] font-bold uppercase tracking-[2px] mb-3" style={{ color: 'var(--text-muted)' }}>
                ✈️ Away Team
              </label>
              <select value={awayId} onChange={e => setAwayId(e.target.value)}
                      className="select-dark w-full px-5 py-4 rounded-xl text-sm font-medium">
                <option value="">Select away team...</option>
                {teams.map(t => <option key={t.team_id} value={t.team_id}>{t.name} ({t.abbreviation})</option>)}
              </select>
            </div>
          </div>

          <button onClick={handlePredict} disabled={loading}
                  className="btn-accent w-full py-5 rounded-xl text-sm disabled:opacity-50">
            {loading ? '⏳ Running Model...' : '⚡ RUN PREDICTION'}
          </button>

          {error && (
            <div className="mt-6 px-5 py-3 rounded-xl text-sm font-medium"
                 style={{ background: 'var(--danger-bg)', color: 'var(--danger)' }}>{error}</div>
          )}

          {prediction && (
            <div className="animate-fade-in-up" style={{ marginTop: '48px' }}>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-10" style={{ marginBottom: '40px' }}>
                {/* Home */}
                <div className="text-center rounded-2xl" style={{ padding: '40px', background: 'var(--bg-base)', border: '1px solid var(--border)' }}>
                  <div className="w-16 h-16 mx-auto rounded-2xl flex items-center justify-center text-3xl mb-5"
                       style={{ background: 'var(--accent-subtle)' }}>🏀</div>
                  <div className="text-[10px] font-bold uppercase tracking-[2px] mb-2" style={{ color: 'var(--text-muted)' }}>Home</div>
                  <div className="text-lg font-bold mb-2">{prediction.home_team || homeName?.name}</div>
                  <div className="text-5xl font-black mt-3" style={{ color: 'var(--accent)', fontFamily: 'var(--font-heading)' }}>
                    {prediction.home_win_pct}%
                  </div>
                  <div className="text-xs mt-3" style={{ color: 'var(--text-muted)' }}>
                    Score: {Number(prediction.home_team_score).toFixed(1)}
                  </div>
                </div>

                {/* VS */}
                <div className="flex flex-col items-center justify-center gap-8">
                  <div className="text-5xl font-black italic" style={{ color: 'var(--text-dim)', fontFamily: 'var(--font-heading)' }}>VS</div>
                  <div className="w-full rounded-xl text-center" style={{ padding: '20px', background: 'var(--bg-base)', border: '1px solid var(--border)' }}>
                    <div className="text-[10px] font-bold uppercase tracking-[2px] mb-1" style={{ color: 'var(--text-muted)' }}>H2H</div>
                    <div className="text-xl font-black">{(prediction.h2h_win_pct * 100).toFixed(1)}%</div>
                    <div className="text-[10px] mt-1" style={{ color: 'var(--text-muted)' }}>Home advantage</div>
                  </div>
                  <div className="tag" style={{
                    background: prediction.home_win_pct > prediction.away_win_pct ? 'var(--accent-subtle)' : 'var(--purple-bg)',
                    color: prediction.home_win_pct > prediction.away_win_pct ? 'var(--accent)' : 'var(--purple)',
                  }}>
                    🏆 {prediction.home_win_pct > prediction.away_win_pct ? (prediction.home_team || homeName?.name) : (prediction.away_team || awayName?.name)} FAVORED
                  </div>
                </div>

                {/* Away */}
                <div className="text-center rounded-2xl" style={{ padding: '40px', background: 'var(--bg-base)', border: '1px solid var(--border)' }}>
                  <div className="w-16 h-16 mx-auto rounded-2xl flex items-center justify-center text-3xl mb-5"
                       style={{ background: 'var(--purple-bg)' }}>🏀</div>
                  <div className="text-[10px] font-bold uppercase tracking-[2px] mb-2" style={{ color: 'var(--text-muted)' }}>Away</div>
                  <div className="text-lg font-bold mb-2">{prediction.away_team || awayName?.name}</div>
                  <div className="text-5xl font-black mt-3" style={{ color: 'var(--purple)', fontFamily: 'var(--font-heading)' }}>
                    {prediction.away_win_pct}%
                  </div>
                  <div className="text-xs mt-3" style={{ color: 'var(--text-muted)' }}>
                    Score: {Number(prediction.away_team_score).toFixed(1)}
                  </div>
                </div>
              </div>

              <div className="rounded-2xl flex flex-col gap-4"
                   style={{ padding: '36px', background: 'var(--bg-base)', border: '1px solid var(--border)' }}>
                <div className="text-[10px] font-bold uppercase tracking-[2px] mb-2" style={{ color: 'var(--text-muted)' }}>
                  Win Probability Breakdown
                </div>
                <PredictionBar label={prediction.home_team?.split(' ').pop() || (homeName?.abbreviation && homeName.abbreviation !== 'nan' ? homeName.abbreviation : homeName?.name?.substring(0, 3).toUpperCase()) || 'HOME'}
                               percentage={prediction.home_win_pct} color="var(--accent)" />
                <PredictionBar label={prediction.away_team?.split(' ').pop() || (awayName?.abbreviation && awayName.abbreviation !== 'nan' ? awayName.abbreviation : awayName?.name?.substring(0, 3).toUpperCase()) || 'AWAY'}
                               percentage={prediction.away_win_pct} color="var(--purple)" delay={300} />
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
