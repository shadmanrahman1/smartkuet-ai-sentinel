import { useState } from 'react';
import { VIDEO_FEED_URL } from '../api/client';

export default function MjpegFeed({ online }) {
  const [imgError, setImgError] = useState(false);

  return (
    <div className="feed-container">
      {online && !imgError ? (
        <>
          <img
            src={VIDEO_FEED_URL}
            alt="Live annotated MJPEG video feed"
            onError={() => setImgError(true)}
          />
          <div className="feed-overlay">
            <span className="badge badge-green">
              <span className="live-dot" /> LIVE FEED
            </span>
          </div>
        </>
      ) : (
        <div className="feed-placeholder">
          <div className="cam-icon">📹</div>
          <div style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>
            CCTV Feed — Demo Mode
          </div>
          <div style={{ fontSize: '0.78rem', maxWidth: 280, textAlign: 'center' }}>
            Start the FastAPI backend on port 8002 to display the live annotated video feed
          </div>
          <div style={{ marginTop: 8 }}>
            <span className="badge badge-muted">OFFLINE</span>
          </div>
          <div style={{ marginTop: 16, fontFamily: 'JetBrains Mono, monospace', fontSize: '0.72rem', color: 'var(--text-muted)', background: 'rgba(0,0,0,0.3)', padding: '8px 16px', borderRadius: 8, border: '1px solid var(--border)' }}>
            uvicorn api.main:app --port 8002
          </div>
        </div>
      )}
    </div>
  );
}
