export default function ExpertPanel({ rankings = [] }) {
  const topTeams = rankings.slice(0, 3);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-2">
        <span className="text-lg">📊</span>
        <h3 className="text-base font-black uppercase tracking-wide" style={{ fontFamily: 'var(--font-heading)' }}>
          Expert Picks
        </h3>
      </div>

      {/* Analyst 1 */}
      <div className="card" style={{ padding: '28px', borderRadius: '16px' }}>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full flex items-center justify-center text-lg" style={{ background: 'var(--bg-elevated)' }}>🧑‍💼</div>
            <div>
              <div className="text-sm font-bold">Marcus Vance</div>
              <div className="text-[10px] font-bold uppercase tracking-widest" style={{ color: 'var(--accent)' }}>PRO ANALYST</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>ROI</div>
            <div className="text-sm font-bold" style={{ color: 'var(--success)' }}>+14.8%</div>
          </div>
        </div>
        <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
          &ldquo;{topTeams[0]?.name || 'Thunder'}&apos;s depth will be tested, but their defense is the best in the league. Lean into the over tonight.&rdquo;
        </p>
      </div>

      {/* Analyst 2 */}
      <div className="card" style={{ padding: '28px', borderRadius: '16px' }}>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full flex items-center justify-center text-lg" style={{ background: 'var(--bg-elevated)' }}>👩‍🔬</div>
            <div>
              <div className="text-sm font-bold">Sarah Chen</div>
              <div className="text-[10px] font-bold uppercase tracking-widest" style={{ color: 'var(--purple)' }}>DATA SCIENTIST</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-[10px]" style={{ color: 'var(--text-muted)' }}>Win Rate</div>
            <div className="text-sm font-bold" style={{ color: 'var(--success)' }}>72%</div>
          </div>
        </div>
        <p className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
          &ldquo;The model suggests a 4-point swing toward {topTeams[1]?.name || 'Cavaliers'}. Current public money is chasing the favorite incorrectly.&rdquo;
        </p>
      </div>

      {/* View All */}
      <button className="w-full py-4 rounded-xl text-xs font-bold uppercase tracking-widest cursor-pointer transition-all duration-300"
              style={{ background: 'var(--bg-surface)', color: 'var(--text-secondary)', border: '1px solid var(--border)' }}>
        View All Analysis
      </button>

      {/* Trending */}
      <div className="card" style={{ padding: '28px', borderRadius: '16px', marginTop: '8px' }}>
        <div className="flex items-center justify-between mb-5">
          <span className="text-[10px] font-black uppercase tracking-[2px]" style={{ color: 'var(--accent)' }}>
            Trending Sharp Money
          </span>
          <span>📈</span>
        </div>
        {topTeams.map((team, i) => (
          <div key={i} className="flex items-center justify-between"
               style={{ padding: '12px 0', borderTop: i > 0 ? '1px solid var(--border)' : 'none' }}>
            <span className="text-sm font-bold">{team.name}</span>
            <span className="text-sm font-bold" style={{ color: 'var(--success)' }}>
              ↑ {(Math.random() * 15 + 5).toFixed(0)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
