export default function TrackingPanel({ tracking, online }) {
  const tracks = tracking?.active_tracks || [];
  const totalSeen = tracking?.total_tracks_seen ?? 0;
  const activeCount = tracking?.active_track_count ?? 0;

  return (
    <div className="card card-flat" style={{ height: '100%' }}>
      <div className="flex items-center justify-between" style={{ marginBottom: 16 }}>
        <h4 style={{ color: 'var(--text-primary)' }}>🎯 Active Tracks</h4>
        <span className={`badge ${online ? 'badge-green' : 'badge-muted'}`}>
          {online ? 'LIVE' : 'DEMO'}
        </span>
      </div>

      <div className="grid-2" style={{ marginBottom: 16 }}>
        <div style={{ textAlign: 'center' }}>
          <div className="stat-number" style={{ fontSize: '2rem' }}>{activeCount}</div>
          <div className="stat-label">Active</div>
        </div>
        <div style={{ textAlign: 'center' }}>
          <div className="stat-number" style={{ fontSize: '2rem' }}>{totalSeen}</div>
          <div className="stat-label">Total Seen</div>
        </div>
      </div>

      <div className="divider" />

      {tracks.length === 0 ? (
        <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', padding: '16px 0' }}>
          No active tracks
        </div>
      ) : (
        <div className="flex-col gap-2">
          {tracks.slice(0, 6).map(t => (
            <div key={t.track_id} className="flex items-center justify-between" style={{
              padding: '8px 12px',
              background: 'rgba(0,212,170,0.05)',
              borderRadius: 8,
              border: '1px solid rgba(0,212,170,0.1)',
            }}>
              <span className="track-chip">ID {t.track_id}</span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                {t.age_seconds?.toFixed(1)}s
              </span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                {Math.round((t.confidence ?? 0) * 100)}%
              </span>
            </div>
          ))}
        </div>
      )}

      <div className="divider" />
      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        Tracker: <span className="mono" style={{ color: 'var(--accent)' }}>{tracking?.tracker_type || 'iou_fallback'}</span>
      </div>
    </div>
  );
}
