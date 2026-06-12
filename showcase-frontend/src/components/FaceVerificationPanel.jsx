import { useState, useEffect } from 'react';

const STATUS_META = {
  VERIFIED_KNOWN_MEMBER: { icon: '✅', label: 'Known Demo Member', color: 'green' },
  UNKNOWN_VISITOR:        { icon: '🚫', label: 'Unknown Visitor',   color: 'red' },
  LOW_CONFIDENCE:         { icon: '⚠️', label: 'Low Confidence',   color: 'yellow' },
  NO_FACE_DETECTED:       { icon: '👤', label: 'No Face Detected',  color: 'grey' },
  MODEL_UNAVAILABLE:      { icon: '🔧', label: 'Model Unavailable', color: 'grey' },
  GALLERY_EMPTY:          { icon: '📂', label: 'Gallery Empty',      color: 'grey' },
  ERROR:                  { icon: '❌', label: 'Error',              color: 'grey' },
};

const COLOR_STYLES = {
  green:  { color: 'var(--green)',  bg: 'var(--green-bg)',  border: 'rgba(34,197,94,0.3)' },
  red:    { color: 'var(--red)',    bg: 'var(--red-bg)',    border: 'rgba(239,68,68,0.3)' },
  yellow: { color: 'var(--yellow)', bg: 'var(--yellow-bg)', border: 'rgba(245,158,11,0.3)' },
  grey:   { color: 'var(--text-muted)', bg: 'rgba(100,116,139,0.08)', border: 'rgba(100,116,139,0.2)' },
};

export default function FaceVerificationPanel({ online }) {
  const [status, setStatus]     = useState(null);
  const [members, setMembers]   = useState([]);
  const [result, setResult]     = useState(null);
  const [loading, setLoading]   = useState(false);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    if (!online) return;
    fetch('/api/face/status')
      .then(r => r.json())
      .then(setStatus)
      .catch(() => {});
    fetch('/api/face/demo-members')
      .then(r => r.json())
      .then(d => { setMembers(d.members || []); if (d.members?.length) setSelected(d.members[0]); })
      .catch(() => {});
  }, [online]);

  const handleVerify = async () => {
    if (!selected || !online) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch('/api/face/verify-image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_path: `data/demo_face_gallery/${selected}/img_0.jpg` }),
      });
      const data = await res.json();
      setResult(data);
    } catch {
      setResult({ status: 'ERROR', display_color: 'grey', instruction: 'API call failed.' });
    } finally {
      setLoading(false);
    }
  };

  const statusMeta = result ? (STATUS_META[result.status] || STATUS_META.ERROR) : null;
  const colorStyle = result ? (COLOR_STYLES[result.display_color] || COLOR_STYLES.grey) : null;

  return (
    <div className="card" style={{ marginTop: 24 }}>
      {/* Header */}
      <div className="flex items-center justify-between" style={{ marginBottom: 16 }}>
        <h4>🔍 Face Verification — Demo Prototype</h4>
        <span className={`badge ${online && status?.model_loaded ? 'badge-green' : 'badge-muted'}`}>
          {!online ? 'OFFLINE' : status?.model_loaded ? '✅ MODEL READY' : '⚠️ MODEL NOT LOADED'}
        </span>
      </div>

      {/* Privacy note */}
      <div style={{
        background: 'rgba(0,212,170,0.05)',
        border: '1px solid rgba(0,212,170,0.15)',
        borderRadius: 8,
        padding: '8px 14px',
        fontSize: '0.78rem',
        color: 'var(--text-secondary)',
        marginBottom: 16,
      }}>
        🔒 <strong>Open-source demo data only.</strong> Enrolled gallery = LFW academic identities
        labeled "Demo Member A/B/C". Not real KUET data. Guard makes all final decisions.
      </div>

      {/* Demo member selector */}
      {members.length > 0 ? (
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Select enrolled demo member to verify:
          </div>
          <div className="flex gap-2" style={{ flexWrap: 'wrap' }}>
            {members.map(m => (
              <button
                key={m}
                onClick={() => setSelected(m)}
                className="btn btn-outline"
                style={{
                  padding: '6px 14px',
                  fontSize: '0.82rem',
                  background: selected === m ? 'var(--accent-dim)' : 'transparent',
                  borderColor: selected === m ? 'var(--accent)' : undefined,
                  color: selected === m ? 'var(--accent)' : undefined,
                }}
              >
                {m}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div style={{ marginBottom: 16, fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          {online
            ? '📂 No demo members enrolled. Run: python scripts/prepare_lfw_demo_gallery.py'
            : '📡 Start backend to load demo members.'}
        </div>
      )}

      {/* Verify button */}
      <button
        className="btn btn-primary w-full"
        style={{ justifyContent: 'center', marginBottom: 16, opacity: (!selected || !online || loading) ? 0.5 : 1 }}
        onClick={handleVerify}
        disabled={!selected || !online || loading}
      >
        {loading ? '⏳ Verifying...' : `🔍 Verify ${selected || 'Demo Member'}`}
      </button>

      {/* Result card */}
      {result && statusMeta && colorStyle && (
        <div style={{
          padding: '16px',
          borderRadius: 12,
          border: `1px solid ${colorStyle.border}`,
          background: colorStyle.bg,
          transition: 'all 0.3s ease',
        }}>
          <div className="flex items-center gap-3" style={{ marginBottom: 8 }}>
            <span style={{ fontSize: '1.8rem' }}>{statusMeta.icon}</span>
            <div>
              <div style={{ fontWeight: 800, fontSize: '1rem', color: colorStyle.color }}>
                {statusMeta.label}
              </div>
              {result.matched_member && (
                <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                  Matched: <strong>{result.matched_member}</strong>
                </div>
              )}
            </div>
            {result.confidence > 0 && (
              <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
                <div style={{ fontWeight: 900, fontSize: '1.4rem', color: colorStyle.color }}>
                  {Math.round(result.confidence * 100)}%
                </div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>similarity</div>
              </div>
            )}
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            {result.instruction}
          </div>
          <div style={{ marginTop: 8, fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            {result.processing_ms > 0 && `Processing: ${result.processing_ms.toFixed(1)}ms`}
            {result.face_count > 0 && ` · Faces detected: ${result.face_count}`}
          </div>
        </div>
      )}

      {/* Status detail (when no result yet) */}
      {!result && status && (
        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          Gallery size: <span className="mono" style={{ color: 'var(--accent)' }}>{status.gallery_size}</span> members
          &nbsp;·&nbsp;
          Threshold: <span className="mono" style={{ color: 'var(--accent)' }}>{status.threshold}</span>
          &nbsp;·&nbsp;
          Model: <span className="mono" style={{ color: 'var(--accent)' }}>{status.model_name || 'buffalo_s'}</span>
        </div>
      )}
    </div>
  );
}
