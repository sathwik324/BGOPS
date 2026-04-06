import PredictionBar from './PredictionBar';

export default function MatchCard({ match, prediction, onPredict, featured = false }) {
  const homeTeam = match.home_team || 'Home';
  const awayTeam = match.away_team || 'Away';
  const getAbbr = (abbr, teamName) => (!abbr || String(abbr).toLowerCase() === 'nan') ? teamName.substring(0, 3).toUpperCase() : abbr;
  const homeAbbr = getAbbr(match.home_abbr, homeTeam);
  const awayAbbr = getAbbr(match.away_abbr, awayTeam);
  const date = match.scheduled_date || '';
  const hasPrediction = prediction && prediction.home_win_pct !== undefined;

  if (featured) {
    return (
      <div className="card" style={{ borderRadius: '24px' }}>
        {/* Header */}
        <div className="flex items-center justify-between" style={{ padding: '32px 40px 0' }}>
          <div className="tag" style={{ background: 'var(--accent-subtle)', color: 'var(--accent)', border: '1px solid rgba(255,107,53,0.15)' }}>
            <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: 'var(--accent)' }} />
            MATCHUP OF THE NIGHT
          </div>
          <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{date}</span>
        </div>

        {/* Teams */}
        <div className="flex items-center justify-around" style={{ padding: '48px 40px' }}>
          <div className="flex flex-col items-center flex-1">
            <div className="w-20 h-20 rounded-2xl flex items-center justify-center text-4xl mb-5"
                 style={{ background: 'var(--bg-elevated)' }}>🏀</div>
            <div className="text-3xl font-black tracking-tight mb-1 text-center" style={{ fontFamily: 'var(--font-heading)' }}>{homeAbbr}</div>
            <div className="text-sm text-center" style={{ color: 'var(--text-muted)' }}>{homeTeam}</div>
          </div>
          <div className="flex flex-col items-center gap-3 px-8 justify-center">
            <div className="text-sm font-medium" style={{ color: 'var(--accent)' }}>10:00 PM EST</div>
            <div className="text-4xl font-black italic" style={{ color: 'var(--text-dim)', fontFamily: 'var(--font-heading)' }}>VS</div>
          </div>
          <div className="flex flex-col items-center flex-1">
            <div className="w-20 h-20 rounded-2xl flex items-center justify-center text-4xl mb-5"
                 style={{ background: 'var(--bg-elevated)' }}>🏀</div>
            <div className="text-3xl font-black tracking-tight mb-1 text-center" style={{ fontFamily: 'var(--font-heading)' }}>{awayAbbr}</div>
            <div className="text-sm text-center" style={{ color: 'var(--text-muted)' }}>{awayTeam}</div>
          </div>
        </div>

        {/* Prediction or Button */}
        <div style={{ padding: '0 40px 36px' }}>
          {hasPrediction ? (
            <div className="p-7 rounded-2xl flex flex-col gap-4" style={{ background: 'var(--bg-base)' }}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-bold uppercase tracking-[2px]" style={{ color: 'var(--text-muted)' }}>Win Probability</span>
                <span className="text-sm font-bold" style={{ color: 'var(--accent)' }}>
                  {prediction.home_win_pct > prediction.away_win_pct ? `${prediction.home_win_pct}% ${homeAbbr}` : `${prediction.away_win_pct}% ${awayAbbr}`}
                </span>
              </div>
              <PredictionBar label={homeAbbr} percentage={prediction.home_win_pct} color="var(--accent)" />
              <PredictionBar label={awayAbbr} percentage={prediction.away_win_pct} color="var(--purple)" delay={200} />
            </div>
          ) : (
            <button onClick={() => onPredict?.(match)} className="btn-accent w-full py-4 rounded-xl text-sm">
              ⚡ Lock Prediction
            </button>
          )}
        </div>
      </div>
    );
  }

  /* Compact ticker card */
  return (
    <div className="card flex items-center gap-5 cursor-pointer" style={{ padding: '20px 24px', borderRadius: '16px' }}
         onClick={() => !hasPrediction && onPredict?.(match)}>
      <div className="w-10 h-10 rounded-xl flex items-center justify-center text-lg shrink-0"
           style={{ background: 'var(--bg-elevated)' }}>🏀</div>
      <div className="flex-1 min-w-0">
        <div className="text-sm font-bold truncate">{homeAbbr} vs {awayAbbr}</div>
        <div className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>{homeTeam} vs {awayTeam}</div>
      </div>
      <div className="text-right shrink-0">
        {hasPrediction ? (
          <>
            <div className="text-sm font-bold" style={{ color: 'var(--accent)' }}>{prediction.home_win_pct}%</div>
            <div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{homeAbbr} win</div>
          </>
        ) : (
          <>
            <div className="text-xs font-medium" style={{ color: 'var(--text-secondary)' }}>{date}</div>
            <div className="text-[10px] mt-0.5" style={{ color: 'var(--accent)' }}>Predict →</div>
          </>
        )}
      </div>
    </div>
  );
}
