export default function HeroSection({ topTeams = [] }) {
  return (
    <section className="relative overflow-hidden" style={{ paddingTop: '200px', paddingBottom: '160px' }}>
      {/* Background Effects */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute -top-40 -left-40 w-[500px] h-[500px] rounded-full"
             style={{ background: 'radial-gradient(circle, rgba(255,107,53,0.06) 0%, transparent 70%)' }} />
        <div className="absolute bottom-0 right-0 w-[300px] h-[300px] rounded-full animate-float"
             style={{ background: 'radial-gradient(circle, rgba(139,92,246,0.04) 0%, transparent 70%)' }} />
      </div>

      <div className="page-container relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-20 items-center">
          {/* Left */}
          <div>
            <div className="tag mb-10 animate-fade-in-up stagger-1"
                 style={{ background: 'var(--accent-subtle)', color: 'var(--accent)', border: '1px solid rgba(255,107,53,0.15)' }}>
              <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: 'var(--accent)' }} />
              FEATURED PREDICTOR · MATCHDAY 24
            </div>

            <h1 className="animate-fade-in-up stagger-2"
                style={{
                  fontFamily: 'var(--font-heading)',
                  fontSize: 'clamp(3rem, 6vw, 5.5rem)',
                  fontWeight: 900,
                  lineHeight: 0.95,
                  letterSpacing: '-2px',
                  marginBottom: '2.5rem',
                }}>
              <span style={{ color: 'var(--text-primary)' }}>THE</span><br />
              <span style={{ color: 'var(--text-primary)' }}>PREDICTORS</span><br />
              <span style={{
                background: 'linear-gradient(135deg, var(--accent), var(--accent-light))',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}>HUB</span>
            </h1>

            <p className="text-base leading-relaxed max-w-[460px] animate-fade-in-up stagger-3"
               style={{ color: 'var(--text-secondary)', lineHeight: 1.8, marginBottom: '3rem' }}>
              Harness the data. Master the spread. Join the elite network of NBA
              analysts making high-stakes calls tonight.
            </p>

            <div className="flex items-center gap-4 animate-fade-in-up stagger-4">
              <a href="#predictions"
                 className="btn-accent px-7 py-3.5 rounded-xl text-[13px] inline-flex items-center gap-2">
                View Predictions
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M7 17L17 7M17 7H7M17 7V17" />
                </svg>
              </a>
              <a href="#leaderboard"
                 className="px-7 py-3.5 rounded-xl text-[13px] font-semibold inline-flex items-center gap-2 transition-all duration-300"
                 style={{ background: 'var(--bg-surface)', color: 'var(--text-primary)', border: '1px solid var(--border-light)' }}>
                🏆 Leaderboard
              </a>
            </div>
          </div>

          {/* Right: Stats Cards */}
          <div className="flex flex-col gap-6 animate-slide-right stagger-3">
            <div className="card flex items-center justify-between" style={{ padding: '40px', borderRadius: '24px' }}>
              <div>
                <div className="text-xs font-bold uppercase tracking-[2px] mb-2" style={{ color: 'var(--accent)' }}>
                  Global Accuracy
                </div>
                <div className="text-5xl font-black" style={{ fontFamily: 'var(--font-heading)' }}>
                  84.2<span className="text-2xl" style={{ color: 'var(--text-muted)' }}>%</span>
                </div>
              </div>
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-xl"
                   style={{ background: 'var(--accent-subtle)' }}>📊</div>
            </div>

            <div className="card flex items-center justify-between" style={{ padding: '40px', borderRadius: '24px' }}>
              <div>
                <div className="text-xs font-bold uppercase tracking-[2px] mb-2" style={{ color: 'var(--purple)' }}>
                  Active Matchups
                </div>
                <div className="text-5xl font-black" style={{ fontFamily: 'var(--font-heading)' }}>
                  {topTeams.length || 30}
                </div>
              </div>
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-xl"
                   style={{ background: 'var(--purple-bg)' }}>🎯</div>
            </div>

            <div className="card" style={{ padding: '40px', borderRadius: '24px' }}>
              <div className="text-xs font-bold uppercase tracking-[2px] mb-4" style={{ color: 'var(--success)' }}>
                #1 Ranked Team
              </div>
              {topTeams[0] ? (
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold mb-1">{topTeams[0].name}</div>
                    <div className="text-base" style={{ color: 'var(--text-muted)' }}>
                      {topTeams[0].wins}W - {topTeams[0].losses}L
                    </div>
                  </div>
                  <div className="text-5xl font-black" style={{ color: 'var(--success)', fontFamily: 'var(--font-heading)' }}>
                    {(topTeams[0].win_ratio * 100).toFixed(0)}%
                  </div>
                </div>
              ) : (
                <div className="text-base" style={{ color: 'var(--text-muted)' }}>Loading...</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
