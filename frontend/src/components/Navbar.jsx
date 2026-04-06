export default function Navbar() {
  const links = ['Games', 'Predictions', 'Stats', 'Leaderboard'];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50"
         style={{
           background: 'rgba(8,8,12,0.8)',
           backdropFilter: 'blur(20px)',
           borderBottom: '1px solid var(--border)',
         }}>
      <div className="page-container h-20 flex items-center justify-between">
        {/* Logo */}
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

        {/* Nav */}
        <div className="hidden md:flex items-center gap-1">
          {links.map((item, i) => (
            <a key={item}
               href={`#${item.toLowerCase()}`}
               className="px-5 py-2 rounded-lg text-[13px] font-medium transition-all duration-300"
               style={{
                 color: i === 1 ? 'var(--accent)' : 'var(--text-secondary)',
                 background: i === 1 ? 'var(--accent-subtle)' : 'transparent',
               }}>
              {item}
            </a>
          ))}
        </div>

        {/* Avatar */}
        <div className="w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold"
             style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)' }}>
          S
        </div>
      </div>
    </nav>
  );
}
