export default function Leaderboard({ rankings = [] }) {
  const top = rankings.slice(0, 10);

  return (
    <section id="leaderboard" style={{ paddingTop: '100px', paddingBottom: '100px' }}>
      <div className="page-container">
        {/* Header */}
        <div className="flex items-center justify-between" style={{ marginBottom: '48px' }}>
          <div className="flex items-center gap-4">
            <div className="w-1.5 h-10 rounded-full" style={{ background: 'var(--accent)' }} />
            <div>
              <h2 className="text-2xl font-black uppercase tracking-tight" style={{ fontFamily: 'var(--font-heading)' }}>
                Team Leaderboard
              </h2>
              <p className="text-sm mt-2" style={{ color: 'var(--text-muted)' }}>
                Power rankings based on system scoring model
              </p>
            </div>
          </div>
          <div className="tag" style={{ background: 'var(--accent-subtle)', color: 'var(--accent)', border: '1px solid rgba(255,107,53,0.15)' }}>
            2025-26 SEASON
          </div>
        </div>

        {/* Table */}
        <div className="card overflow-hidden" style={{ borderRadius: '24px' }}>
          {/* Header */}
          <div className="grid grid-cols-12 gap-3" style={{ padding: '20px 36px', background: 'var(--bg-elevated)' }}>
            {['#', 'TEAM', 'W', 'L', 'WIN %', 'LAST 10', 'POWER SCORE'].map((h, i) => (
              <div key={h}
                   className={`text-[10px] font-bold uppercase tracking-[2px] ${
                     i === 0 ? 'col-span-1'
                     : i === 1 ? 'col-span-3'
                     : i === 5 ? 'col-span-2 text-center'
                     : i === 6 ? 'col-span-2 text-center'
                     : 'col-span-1 text-center'
                   }`} style={{ color: 'var(--text-muted)' }}>
                {h}
              </div>
            ))}
          </div>

          {top.map((team, i) => {
            const winPct = team.win_ratio != null ? (team.win_ratio * 100).toFixed(1) : '0.0';
            const score = team.team_score != null ? Number(team.team_score).toFixed(1) : '0.0';
            const isTop3 = i < 3;

            return (
              <div key={i}
                   className="grid grid-cols-12 gap-3 items-center transition-all duration-300"
                   style={{ padding: '20px 36px', borderTop: '1px solid var(--border)', cursor: 'pointer' }}
                   onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-card-hover)'}
                   onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
                <div className="col-span-1">
                  {isTop3 ? (
                    <div className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black"
                         style={{ background: 'var(--accent)', color: '#fff' }}>{i + 1}</div>
                  ) : (
                    <span className="text-sm font-bold pl-2" style={{ color: 'var(--text-muted)' }}>{i + 1}</span>
                  )}
                </div>
                <div className="col-span-3 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center text-sm shrink-0"
                       style={{ background: 'var(--bg-elevated)' }}>🏀</div>
                  <span className="text-sm font-bold">{team.name}</span>
                </div>
                <div className="col-span-1 text-center text-sm font-bold" style={{ color: 'var(--success)' }}>{team.wins}</div>
                <div className="col-span-1 text-center text-sm font-bold" style={{ color: 'var(--danger)' }}>{team.losses}</div>
                <div className="col-span-1 text-center text-sm font-black">{winPct}%</div>
                <div className="col-span-2 text-center">
                  <span className="text-sm font-bold" style={{ color: 'var(--success)' }}>{team.last_10_wins ?? 0}</span>
                  <span className="mx-1" style={{ color: 'var(--text-dim)' }}>-</span>
                  <span className="text-sm font-bold" style={{ color: 'var(--danger)' }}>{team.last_10_losses ?? 0}</span>
                </div>
                <div className="col-span-2 text-center">
                  <span className="inline-block px-3 py-1.5 rounded-lg text-xs font-black"
                        style={{
                          background: isTop3 ? 'var(--accent-subtle)' : 'var(--bg-elevated)',
                          color: isTop3 ? 'var(--accent)' : 'var(--text-secondary)',
                        }}>{score}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
