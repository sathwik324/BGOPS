export default function PredictionBar({ label, percentage, color = 'var(--accent)', delay = 0 }) {
  return (
    <div className="flex items-center gap-4">
      <span className="text-xs font-bold w-12 text-right shrink-0 uppercase tracking-wider"
            style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-heading)' }}>
        {label}
      </span>
      <div className="flex-1 h-4 rounded-full overflow-hidden"
           style={{ background: 'var(--bg-surface)' }}>
        <div className="h-full rounded-full animate-bar-fill relative"
             style={{
               width: `${percentage}%`,
               background: `linear-gradient(90deg, ${color}, ${color}99)`,
               animationDelay: `${delay}ms`,
               boxShadow: `0 0 16px ${color}33`,
             }}>
          {/* Shimmer effect */}
          <div className="absolute inset-0 rounded-full"
               style={{
                 background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.15) 50%, transparent 100%)',
                 backgroundSize: '200% 100%',
                 animation: 'shimmer 2s ease-in-out infinite',
               }} />
        </div>
      </div>
      <span className="text-base font-black w-16 text-right shrink-0"
            style={{ color, fontFamily: 'var(--font-heading)' }}>
        {percentage}%
      </span>
    </div>
  );
}
