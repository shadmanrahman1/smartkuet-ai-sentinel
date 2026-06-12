import { useState, useEffect } from 'react';
import { fetchRiskFusionStatus } from '../api/client';

const LEVEL_STYLES = {
  LOW:      { color: 'var(--green)',  bg: 'var(--green-bg)',  border: 'rgba(34,197,94,0.3)',  icon: '🟢' },
  MEDIUM:   { color: 'var(--yellow)', bg: 'var(--yellow-bg)', border: 'rgba(245,158,11,0.3)', icon: '🟡' },
  HIGH:     { color: 'var(--orange)', bg: 'var(--orange-bg)', border: 'rgba(249,115,22,0.3)', icon: '🟠' },
  CRITICAL: { color: 'var(--red)',    bg: 'var(--red-bg)',    border: 'rgba(239,68,68,0.3)',   icon: '🔴' }
};

export default function RiskFusionPanel({ online }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    try {
      const res = await fetchRiskFusionStatus();
      setData(res.data);
    } catch {
      // Fallback handled inside api client
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 3000);
    return () => clearInterval(interval);
  }, [online]);

  if (loading || !data) {
    return (
      <div className="card" style={{ marginTop: 24, padding: 24, textAlign: 'center' }}>
        <span style={{ color: 'var(--text-muted)' }}>⏳ Loading Multi-Modal Risk Fusion state...</span>
      </div>
    );
  }

  const currentStyle = LEVEL_STYLES[data.level] || LEVEL_STYLES.MEDIUM;

  // Signal chips logic derived from reasoning trace for explainability
  const getSignalStatus = (type) => {
    const reasonsStr = data.reasons.join(' ').toLowerCase();
    switch (type) {
      case 'camera':
        if (reasonsStr.includes('camera') && (reasonsStr.includes('offline') || reasonsStr.includes('unavailable'))) {
          return { text: '🔴 OFFLINE', border: 'rgba(239,68,68,0.3)', color: 'var(--red)' };
        }
        return { text: '🟢 ONLINE', border: 'rgba(34,197,94,0.3)', color: 'var(--green)' };

      case 'face':
        if (reasonsStr.includes('verified known face')) {
          return { text: '🟢 VERIFIED KNOWN', border: 'rgba(34,197,94,0.3)', color: 'var(--green)' };
        }
        if (reasonsStr.includes('low confidence face')) {
          return { text: '🟡 LOW CONFIDENCE', border: 'rgba(245,158,11,0.3)', color: 'var(--yellow)' };
        }
        if (reasonsStr.includes('unrecognized face') || reasonsStr.includes('unknown face')) {
          return { text: '🔴 UNKNOWN VISITOR', border: 'rgba(239,68,68,0.3)', color: 'var(--red)' };
        }
        return { text: '⚪ NOT DETECTED', border: 'rgba(148,163,184,0.2)', color: 'var(--text-secondary)' };

      case 'object':
        if (reasonsStr.includes('mitigating cue') || reasonsStr.includes('lanyard') || reasonsStr.includes('id card') || reasonsStr.includes('badge')) {
          return { text: '🟢 PRESENT (MITIGATED)', border: 'rgba(34,197,94,0.3)', color: 'var(--green)' };
        }
        return { text: '⚪ NO CUES DETECTED', border: 'rgba(148,163,184,0.2)', color: 'var(--text-secondary)' };

      case 'tracking':
        if (reasonsStr.includes('gate-zone') || reasonsStr.includes('loitering') || reasonsStr.includes('crowding')) {
          return { text: '🟡 ACTIVE ALERT', border: 'rgba(245,158,11,0.3)', color: 'var(--yellow)' };
        }
        return { text: '🟢 ACTIVE (SECURE)', border: 'rgba(34,197,94,0.3)', color: 'var(--green)' };

      case 'gate':
        if (reasonsStr.includes('gate-zone ROI') || reasonsStr.includes('roi')) {
          return { text: '🟡 PRESENT IN ROI', border: 'rgba(245,158,11,0.3)', color: 'var(--yellow)' };
        }
        return { text: '🟢 SECURE', border: 'rgba(34,197,94,0.3)', color: 'var(--green)' };

      case 'rules':
        if (reasonsStr.includes('critical security') || reasonsStr.includes('high-risk') || reasonsStr.includes('alert')) {
          return { text: '🔴 RULE TRIGGERED', border: 'rgba(239,68,68,0.3)', color: 'var(--red)' };
        }
        return { text: '🟢 GREEN STATE', border: 'rgba(34,197,94,0.3)', color: 'var(--green)' };

      default:
        return { text: '⚪ N/A', border: 'rgba(148,163,184,0.2)', color: 'var(--text-secondary)' };
    }
  };

  const signals = [
    { label: 'Camera Health', type: 'camera' },
    { label: 'Face Verification', type: 'face' },
    { label: 'Object Cues', type: 'object' },
    { label: 'Person Tracking', type: 'tracking' },
    { label: 'Gate-zone ROI', type: 'gate' },
    { label: 'Security Rules', type: 'rules' },
  ];

  return (
    <div className="card" style={{ marginTop: 24, borderLeft: `5px solid ${currentStyle.color}` }}>
      {/* Header */}
      <div className="flex items-center justify-between" style={{ marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h3 style={{ color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 8 }}>
            🧠 Multi-Modal Risk Fusion
          </h3>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: 2 }}>
            Explainable advisory risk score · Local/offline processing
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="badge badge-accent">Human-in-the-loop</span>
          <span className="badge badge-muted">Advisory Signal</span>
        </div>
      </div>

      {/* Main Fusion Display Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: 24, marginBottom: 20 }}>
        {/* Score & Verdict Gauges */}
        <div style={{
          background: 'rgba(255,255,255,0.02)',
          border: '1px solid var(--border)',
          borderRadius: 12,
          padding: '20px 16px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '3rem',
            fontWeight: 900,
            lineHeight: 1,
            color: currentStyle.color,
            fontFamily: 'monospace'
          }}>
            {data.score}
            <span style={{ fontSize: '1rem', fontWeight: 500, color: 'var(--text-secondary)' }}>/100</span>
          </div>
          <div style={{
            marginTop: 10,
            padding: '4px 14px',
            borderRadius: 99,
            fontSize: '0.78rem',
            fontWeight: 800,
            color: currentStyle.color,
            background: currentStyle.bg,
            border: `1px solid ${currentStyle.border}`,
            letterSpacing: '0.05em'
          }}>
            {currentStyle.icon} {data.level} RISK
          </div>
          {data.human_review_required && (
            <div style={{
              marginTop: 12,
              fontSize: '0.68rem',
              fontWeight: 700,
              color: 'var(--yellow)',
              background: 'rgba(245,158,11,0.08)',
              padding: '2px 8px',
              borderRadius: 4,
              border: '1px solid rgba(245,158,11,0.2)'
            }}>
              ⚠️ REVIEW REQUIRED
            </div>
          )}
        </div>

        {/* Auditable Reasons & Action */}
        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.04em', marginBottom: 8 }}>
              ⚙️ Fused Advisory Recommendation
            </div>
            <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: 12, lineHeight: 1.4 }}>
              👉 {data.recommended_action}
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.04em', marginBottom: 8 }}>
              🔍 Audit reasoning trace
            </div>
            <ul style={{ paddingLeft: 18, fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              {data.reasons.map((r, i) => (
                <li key={i} style={{ marginBottom: 4 }}>{r}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Divider */}
      <div style={{ height: 1, background: 'rgba(255,255,255,0.05)', margin: '16px 0' }} />

      {/* Target System Signal Verification Grid */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '0.05em', marginBottom: 10 }}>
          📶 Fused System Signals
        </div>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
          gap: 12
        }}>
          {signals.map(sig => {
            const status = getSignalStatus(sig.type);
            return (
              <div key={sig.label} style={{
                background: 'rgba(255,255,255,0.01)',
                border: '1px solid rgba(255,255,255,0.05)',
                borderRadius: 8,
                padding: '10px 14px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '0.8rem'
              }}>
                <span style={{ color: 'var(--text-secondary)' }}>{sig.label}</span>
                <span style={{
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  color: status.color,
                  padding: '2px 8px',
                  borderRadius: 4,
                  background: 'rgba(255,255,255,0.02)',
                  border: `1px solid ${status.border}`
                }}>
                  {status.text}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Safety Policy Info Banner */}
      <div style={{
        background: 'rgba(255,255,255,0.01)',
        border: '1px solid rgba(255,255,255,0.05)',
        borderRadius: 8,
        padding: '10px 16px',
        fontSize: '0.78rem',
        color: 'var(--text-muted)',
        lineHeight: 1.5,
        display: 'flex',
        flexDirection: 'column',
        gap: 2
      }}>
        <div>🔒 <strong>Human-in-the-loop advisory signal:</strong> Risk score does not automatically deny entry. Guard retains full override credentials.</div>
        <div style={{ color: 'rgba(0, 212, 170, 0.4)' }}>{data.privacy_note}</div>
      </div>
    </div>
  );
}
