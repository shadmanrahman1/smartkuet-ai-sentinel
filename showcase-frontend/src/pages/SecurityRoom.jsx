import { useEffect, useState, useCallback } from 'react';
import { fetchSecurityStatus, fetchTrackingLatest } from '../api/client';
import MjpegFeed from '../components/MjpegFeed';
import TrackingPanel from '../components/TrackingPanel';
import { LevelBadge } from '../components/SecurityLevelCard';
import HumanInLoopBanner from '../components/HumanInLoopBanner';

const EVENT_TYPE_LABELS = {
  NORMAL_ACTIVITY:       { icon: '✅', label: 'Normal Activity' },
  CROWDING:              { icon: '👥', label: 'Crowding Detected' },
  LOITERING:             { icon: '⏳', label: 'Loitering Detected' },
  PHONE_VISIBLE_AT_GATE: { icon: '📱', label: 'Phone at Gate' },
  VEHICLE_NEAR_ENTRY:    { icon: '🚗', label: 'Vehicle Near Entry' },
  AFTER_HOURS_ACTIVITY:  { icon: '🌙', label: 'After-Hours Activity' },
  CAMERA_UNAVAILABLE:    { icon: '📵', label: 'Camera Unavailable' },
  HIGH_RISK_COMBINED:    { icon: '🚨', label: 'HIGH RISK COMBINED' },
};

export default function SecurityRoom() {
  const [security, setSecurity] = useState(null);
  const [tracking, setTracking] = useState(null);
  const [online, setOnline] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);

  const refresh = useCallback(async () => {
    const [sec, trk] = await Promise.all([
      fetchSecurityStatus(),
      fetchTrackingLatest(),
    ]);
    setSecurity(sec.data);
    setTracking(sec.online ? trk.data : trk.data);
    setOnline(sec.online);
    setLastUpdate(new Date().toLocaleTimeString());
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 3000);
    return () => clearInterval(interval);
  }, [refresh]);

  const level = security?.latest_level || 'green';
  const eventType = security?.latest_event_type || 'NORMAL_ACTIVITY';
  const instruction = security?.latest_instruction || 'Monitor normally.';
  const events = security?.latest_events || [];
  const eventMeta = EVENT_TYPE_LABELS[eventType] || { icon: '🔵', label: eventType };

  return (
    <div className="section">
      <div className="container">
        {/* ── Header ── */}
        <div className="flex items-center justify-between" style={{ marginBottom: 32, flexWrap: 'wrap', gap: 16 }}>
          <div>
            <span className="section-tag">Security Control Room</span>
            <h2>🖥 Live Monitoring Dashboard</h2>
          </div>
          <div className="flex items-center gap-3" style={{ flexWrap: 'wrap' }}>
            <span className={`badge ${online ? 'badge-green' : 'badge-muted'}`}>
              <span className={`live-dot ${online ? '' : 'offline'}`} />
              {online ? `LIVE · ${lastUpdate}` : 'DEMO MODE'}
            </span>
            <button className="btn btn-outline" onClick={refresh} style={{ padding: '6px 14px', fontSize: '0.82rem' }}>
              ↻ Refresh
            </button>
          </div>
        </div>

        {/* ── Main grid ── */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 24, marginBottom: 24 }}>
          {/* CCTV Feed */}
          <div>
            <MjpegFeed online={online} />
            <div className="flex" style={{ gap: 8, marginTop: 12, flexWrap: 'wrap' }}>
              <span className="badge badge-muted">🗺️ Gate-Zone ROI: {security?.gate_zone_enabled ? 'ON' : 'OFF'}</span>
              <span className="badge badge-muted">⚠️ Crowd threshold: {security?.crowding_person_threshold ?? 4}</span>
              <span className="badge badge-muted">⏳ Loiter: {security?.loiter_seconds ?? 15}s</span>
            </div>
          </div>

          {/* Tracking Panel */}
          <TrackingPanel tracking={tracking} online={online} />
        </div>

        {/* ── Security Status ── */}
        <div className="grid-3" style={{ marginBottom: 24 }}>
          {/* Current Level */}
          <div className={`card level-${level}`} style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: 8 }}>{eventMeta.icon}</div>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', opacity: 0.7, marginBottom: 4 }}>Current Level</div>
            <LevelBadge level={level} />
            <div style={{ marginTop: 12, fontSize: '0.9rem', fontWeight: 600 }}>{eventMeta.label}</div>
            <div style={{ marginTop: 8, fontSize: '0.82rem', opacity: 0.8, lineHeight: 1.5 }}>{instruction}</div>
          </div>

          {/* Detection Counts */}
          <div className="card">
            <h4 style={{ marginBottom: 16, color: 'var(--text-primary)' }}>📊 Detections</h4>
            {[
              { label: 'Persons (Track)', val: tracking?.active_track_count ?? 0, color: 'var(--accent)' },
              { label: 'Total Seen', val: tracking?.total_tracks_seen ?? 0, color: 'var(--text-secondary)' },
              { label: 'Security Events', val: events.length, color: events.length > 1 ? 'var(--yellow)' : 'var(--green)' },
            ].map(item => (
              <div key={item.label} className="flex items-center justify-between" style={{ marginBottom: 12 }}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{item.label}</span>
                <span style={{ fontWeight: 800, fontSize: '1.4rem', color: item.color }}>{item.val}</span>
              </div>
            ))}
          </div>

          {/* Config */}
          <div className="card">
            <h4 style={{ marginBottom: 16, color: 'var(--text-primary)' }}>⚙️ Engine Config</h4>
            <div className="flex-col gap-2">
              {[
                { k: 'Rules Enabled', v: security?.rules_enabled ? '✅ Yes' : '❌ No' },
                { k: 'Gate-Zone', v: security?.gate_zone_enabled ? '✅ Active' : '⬜ Disabled' },
                { k: 'Crowd Threshold', v: `${security?.crowding_person_threshold ?? 4} persons` },
                { k: 'Loiter Time', v: `${security?.loiter_seconds ?? 15}s` },
              ].map(row => (
                <div key={row.k} className="flex items-center justify-between" style={{ fontSize: '0.82rem', padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>{row.k}</span>
                  <span style={{ fontWeight: 600 }}>{row.v}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── Recent Events ── */}
        {events.length > 0 && (
          <div className="card" style={{ marginBottom: 24 }}>
            <h4 style={{ marginBottom: 16 }}>📋 Current Security Events</h4>
            <div className="flex-col gap-2">
              {events.slice(0, 5).map((ev, i) => {
                const meta = EVENT_TYPE_LABELS[ev.event_type] || { icon: '🔵', label: ev.event_type };
                return (
                  <div key={i} className={`flex items-center justify-between card card-sm level-${ev.level}`} style={{ padding: '10px 16px' }}>
                    <div className="flex items-center gap-3">
                      <span>{meta.icon}</span>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{meta.label}</div>
                        <div style={{ fontSize: '0.78rem', opacity: 0.8 }}>{ev.instruction}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {ev.related_track_ids?.slice(0, 3).map(id => (
                        <span key={id} className="track-chip">ID {id}</span>
                      ))}
                      <LevelBadge level={ev.level} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <HumanInLoopBanner />
      </div>
    </div>
  );
}
