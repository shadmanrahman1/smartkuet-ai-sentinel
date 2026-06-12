import { useState, useEffect } from 'react';
import { fetchObjectCuesStatus } from '../api/client';

export default function ObjectCuesPanel({ online }) {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    fetchObjectCuesStatus()
      .then(res => setStatus(res.data))
      .catch(() => {});
  }, [online]);

  const cueLabels = {
    id_card: 'ID Card',
    lanyard: 'Lanyard',
    visitor_badge: 'Visitor Badge',
    bag: 'Bag',
    helmet: 'Helmet'
  };

  const getStatusBadge = () => {
    if (!status) return { text: 'LOADING', className: 'badge-muted' };
    switch (status.status) {
      case 'READY':
        return { text: '✅ READY', className: 'badge-green' };
      case 'MODEL_NOT_CONFIGURED':
        return { text: '⚠️ MODEL MISSING', className: 'badge-yellow' };
      case 'DISABLED':
      default:
        return { text: 'DISABLED', className: 'badge-muted' };
    }
  };

  const badge = getStatusBadge();

  return (
    <div className="card" style={{ marginTop: 24 }}>
      {/* Header */}
      <div className="flex items-center justify-between" style={{ marginBottom: 16 }}>
        <h4>🎒 Object Cues — Local AI</h4>
        <span className={`badge ${badge.className}`}>
          {badge.text}
        </span>
      </div>

      {/* Safety and validation framing */}
      <div style={{
        background: 'rgba(245,158,11,0.03)',
        border: '1px solid rgba(245,158,11,0.15)',
        borderRadius: 8,
        padding: '8px 14px',
        fontSize: '0.78rem',
        color: 'var(--text-secondary)',
        marginBottom: 16,
      }}>
        ⚠️ <strong>Supporting visual evidence only.</strong> Does not prove KUET membership. Identity check remains InsightFace/LFW face verification.
      </div>

      {/* Supported cues list */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Supported target object cues:
        </div>
        <div className="flex gap-2" style={{ flexWrap: 'wrap' }}>
          {(status?.supported_cues || ['id_card', 'lanyard', 'visitor_badge', 'bag', 'helmet']).map(cue => (
            <span
              key={cue}
              style={{
                padding: '4px 10px',
                borderRadius: 6,
                fontSize: '0.78rem',
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.1)',
                color: 'var(--text-secondary)',
              }}
            >
              {cueLabels[cue] || cue}
            </span>
          ))}
        </div>
      </div>

      {/* Status Instruction Display */}
      <div style={{
        padding: '12px 14px',
        borderRadius: 8,
        background: 'rgba(255,255,255,0.02)',
        border: '1px solid rgba(255,255,255,0.05)',
        fontSize: '0.82rem',
        color: 'var(--text-muted)',
      }}>
        {status?.status === 'DISABLED' && (
          <div style={{ color: 'var(--text-muted)' }}>
            ℹ️ Local object-cue model is not configured yet. Research scaffold is ready.
          </div>
        )}
        {status?.status === 'MODEL_NOT_CONFIGURED' && (
          <div style={{ color: 'var(--yellow)' }}>
            🔧 Add a local YOLO-compatible model at <code className="mono">models/object_cues/best.pt</code> to enable.
          </div>
        )}
        {status?.status === 'READY' && (
          <div style={{ color: 'var(--green)' }}>
            🟢 Object cue model is ready and loaded. Local offline inference is available.
          </div>
        )}
      </div>
    </div>
  );
}
