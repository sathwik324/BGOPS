export default function TopPlayers({ players = [] }) {
  const top = players.slice(0, 10);

  return (
    <section id="stats" style={{ paddingTop: '100px', paddingBottom: '100px' }}>
      <div className="page-container">
        {/* Header */}
        <div className="flex items-center gap-4" style={{ marginBottom: '48px' }}>
          <div className="w-1.5 h-10 rounded-full" style={{ background: 'var(--purple)' }} />
          <div>
            <h2 className="text-2xl font-black uppercase tracking-tight" style={{ fontFamily: 'var(--font-heading)' }}>
              MVP Tracker
            </h2>
            <p className="text-sm mt-2" style={{ color: 'var(--text-muted)' }}>
              Top performers ranked by impact score
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
          {top.map((p, i) => (
            <div key={i} className="card relative" style={{ padding: '28px', borderRadius: '20px' }}>
              <div className="absolute top-4 right-4 w-8 h-8 rounded-xl flex items-center justify-center text-xs font-black"
                   style={{
                     background: i < 3 ? 'var(--accent)' : 'var(--bg-elevated)',
                     color: i < 3 ? '#fff' : 'var(--text-muted)',
                   }}>{i + 1}</div>

              <div className="text-lg font-bold mb-1 leading-tight mt-6">{p.full_name}</div>
              <div className="text-xs mb-8" style={{ color: 'var(--text-muted)' }}>{p.team_name}</div>

              <div className="text-3xl font-black mb-6"
                   style={{ color: 'var(--accent)', fontFamily: 'var(--font-heading)' }}>
                {Number(p.player_score).toFixed(2)}
              </div>

              <div className="grid grid-cols-3 gap-3 pt-5" style={{ borderTop: '1px solid var(--border)' }}>
                {[
                  { label: 'PTS', val: p.points_per_game, color: 'var(--accent)' },
                  { label: 'AST', val: p.assists_per_game, color: 'var(--purple)' },
                  { label: 'REB', val: p.rebounds_per_game, color: 'var(--success)' },
                ].map(s => (
                  <div key={s.label} className="text-center">
                    <div className="text-sm font-bold" style={{ color: s.color }}>{Number(s.val).toFixed(1)}</div>
                    <div className="text-[9px] font-semibold uppercase tracking-widest mt-1" style={{ color: 'var(--text-dim)' }}>{s.label}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
