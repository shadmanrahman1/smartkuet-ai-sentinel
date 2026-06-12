import { useEffect, useState, useCallback } from 'react';
import { fetchSecurityStatus } from '../api/client';
import { SecurityLevelCard } from '../components/SecurityLevelCard';
import HumanInLoopBanner from '../components/HumanInLoopBanner';
import FaceVerificationPanel from '../components/FaceVerificationPanel';
import ObjectCuesPanel from '../components/ObjectCuesPanel';

const ACTION_HISTORY = [
  { time: '14:22', action: 'ALLOW',     note: 'KUET ID verified', color: 'var(--green)' },
  { time: '14:18', action: 'VERIFY ID', note: 'Unknown visitor',   color: 'var(--yellow)' },
  { time: '14:09', action: 'ALLOW',     note: 'Staff member',      color: 'var(--green)' },
];

export default function GuardView() {
  const [security, setSecurity] = useState(null);
  const [online, setOnline] = useState(false);
  const [lastAction, setLastAction] = useState(null);

  const refresh = useCallback(async () => {
    const { data, online: o } = await fetchSecurityStatus();
    setSecurity(data);
    setOnline(o);
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 4000);
    return () => clearInterval(interval);
  }, [refresh]);

  const level = security?.latest_level || 'green';
  const eventType = security?.latest_event_type || 'NORMAL_ACTIVITY';
  const instruction = security?.latest_instruction || 'Monitor normally.';
  const confidence = security?.latest_events?.[0]?.confidence ?? 0.7;
  const trackIds = security?.latest_events?.[0]?.related_track_ids || [];

  const handleAction = (action) => {
    setLastAction({ action, time: new Date().toLocaleTimeString() });
  };

  return (
    <div className="section">
      <div className="container" style={{ maxWidth: 960 }}>
        {/* ── Header ── */}
        <div style={{ marginBottom: 32 }}>
          <span className="section-tag">Guard Decision Assistant</span>
          <div className="flex items-center justify-between" style={{ flexWrap: 'wrap', gap: 12 }}>
            <h2>🛡 Campus Gate Control</h2>
            <span className={`badge ${online ? 'badge-green' : 'badge-muted'}`}>
              <span className={`live-dot ${online ? '' : 'offline'}`} />
              {online ? 'LIVE' : 'DEMO'}
            </span>
          </div>
          <p style={{ color: 'var(--text-secondary)', marginTop: 8, fontSize: '0.9rem' }}>
            AI recommendations are advisory only. You make the final decision.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
          {/* Security Level */}
          <SecurityLevelCard
            level={level}
            eventType={eventType}
            instruction={instruction}
            confidence={confidence}
          />

          {/* Guard Actions */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <h4 style={{ marginBottom: 6 }}>🎯 Related Tracks</h4>
              <div className="flex" style={{ gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
                {trackIds.length > 0
                  ? trackIds.map(id => <span key={id} className="track-chip">ID {id}</span>)
                  : <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No specific tracks flagged</span>}
              </div>
              <h4 style={{ marginBottom: 16 }}>🚦 Gate Actions</h4>
            </div>

            <div className="flex-col gap-3">
              <button
                className="btn btn-green w-full"
                style={{ justifyContent: 'center', padding: '14px', fontSize: '1rem' }}
                onClick={() => handleAction('ALLOW')}
              >
                ✅ ALLOW ENTRY
              </button>
              <button
                className="btn btn-yellow w-full"
                style={{ justifyContent: 'center', padding: '14px', fontSize: '1rem' }}
                onClick={() => handleAction('VERIFY ID')}
              >
                🪪 VERIFY ID
              </button>
              <button
                className="btn btn-red w-full"
                style={{ justifyContent: 'center', padding: '14px', fontSize: '1rem' }}
                onClick={() => handleAction('DENY')}
              >
                🚫 DENY ENTRY
              </button>
            </div>

            {lastAction && (
              <div style={{ marginTop: 16, padding: '10px 14px', background: 'rgba(0,212,170,0.06)', borderRadius: 8, border: '1px solid var(--border)', fontSize: '0.82rem' }}>
                ✔ Last action: <strong>{lastAction.action}</strong> at {lastAction.time}
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'block', marginTop: 2 }}>
                  (Display only — connect backend to persist)
                </span>
              </div>
            )}
          </div>
        </div>

        {/* ── Gate Configuration ── */}
        <div className="grid-3" style={{ marginBottom: 24 }}>
          {[
            { icon: '🗺️', label: 'Gate Zone ROI', val: security?.gate_zone_enabled ? 'Active' : 'Disabled', ok: security?.gate_zone_enabled },
            { icon: '👥', label: 'Crowd Threshold', val: `${security?.crowding_person_threshold ?? 4} persons`, ok: true },
            { icon: '⏳', label: 'Loiter Detection', val: `${security?.loiter_seconds ?? 15}s`, ok: true },
          ].map(item => (
            <div key={item.label} className="card card-sm flex items-center gap-3">
              <span style={{ fontSize: '1.4rem' }}>{item.icon}</span>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{item.label}</div>
                <div style={{ fontWeight: 700, color: item.ok ? 'var(--accent)' : 'var(--text-secondary)' }}>{item.val}</div>
              </div>
            </div>
          ))}
        </div>

        {/* ── Action History ── */}
        <div className="card" style={{ marginBottom: 24 }}>
          <h4 style={{ marginBottom: 16 }}>📋 Recent Actions (Demo)</h4>
          <div className="flex-col gap-2">
            {ACTION_HISTORY.map((a, i) => (
              <div key={i} className="flex items-center gap-4" style={{ padding: '8px 0', borderBottom: '1px solid var(--border)', fontSize: '0.88rem' }}>
                <span className="mono" style={{ color: 'var(--text-muted)', minWidth: 48 }}>{a.time}</span>
                <span style={{ fontWeight: 700, color: a.color, minWidth: 90 }}>{a.action}</span>
                <span style={{ color: 'var(--text-secondary)' }}>{a.note}</span>
              </div>
            ))}
          </div>
        </div>

        <HumanInLoopBanner message="Gate control decisions (ALLOW / VERIFY ID / DENY) are the sole responsibility of the human security guard. AI alerts are advisory inputs only." />

        {/* ── Verification & Object Cue Prototypes ── */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, flexWrap: 'wrap' }}>
          <FaceVerificationPanel online={online} />
          <ObjectCuesPanel online={online} />
        </div>
      </div>
    </div>
  );
}
