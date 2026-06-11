const LEVEL_ICONS = { green: '🟢', yellow: '🟡', orange: '🟠', red: '🔴' };
const LEVEL_EMOJI = { green: '✅', yellow: '⚠️', orange: '🚨', red: '🔴' };

export function SecurityLevelCard({ level = 'green', eventType = 'NORMAL_ACTIVITY', instruction = 'Monitor normally.', confidence = 0.7 }) {
  return (
    <div className={`level-card-big card level-${level}`}>
      <div style={{ fontSize: '3rem', marginBottom: 8 }}>{LEVEL_EMOJI[level]}</div>
      <div style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 8, opacity: 0.7 }}>
        Security Level
      </div>
      <div style={{ fontSize: '2rem', fontWeight: 900, marginBottom: 12, textTransform: 'uppercase' }}>
        {level}
      </div>
      <div className="badge" style={{ marginBottom: 16, fontSize: '0.78rem', background: 'rgba(0,0,0,0.2)', borderColor: 'rgba(255,255,255,0.15)', color: 'inherit', justifyContent: 'center' }}>
        {eventType.replace(/_/g, ' ')}
      </div>
      <p style={{ fontSize: '0.95rem', opacity: 0.9, lineHeight: 1.5 }}>{instruction}</p>
      <div style={{ marginTop: 16, fontSize: '0.78rem', opacity: 0.6 }}>
        Confidence: {Math.round(confidence * 100)}%
      </div>
    </div>
  );
}

export function LevelBadge({ level = 'green' }) {
  return (
    <span className={`badge level-${level}`}>
      {LEVEL_ICONS[level]} {level.toUpperCase()}
    </span>
  );
}
