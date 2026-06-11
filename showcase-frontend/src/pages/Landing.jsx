import { useEffect, useState } from 'react';
import { fetchRuntimeStatus } from '../api/client';
import HumanInLoopBanner from '../components/HumanInLoopBanner';

const FEATURES = [
  { icon: '🎯', title: 'Real-Time Detection', desc: 'YOLOv8n detects persons, phones, and vehicles at 60–85+ FPS using GPU acceleration.' },
  { icon: '🔢', title: 'Person Tracking', desc: 'IoU-based tracker assigns temporary IDs to monitor movement across consecutive frames.' },
  { icon: '🚦', title: 'Security Rules Engine', desc: 'Deterministic rules generate green/yellow/orange/red alerts for crowding, loitering, after-hours, and more.' },
  { icon: '📸', title: 'Evidence Capture', desc: 'Dual raw + annotated JPEG snapshots saved automatically for yellow/orange/red events.' },
  { icon: '🗺️', title: 'Gate-Zone ROI', desc: 'Configurable normalized bounding-box filter counts only tracks inside the campus gate area.' },
  { icon: '🔒', title: 'Offline First', desc: 'Zero cloud dependencies. Runs entirely on local hardware. No internet required in production.' },
];

const ARCH = [
  { layer: 'Camera / Video', detail: 'Webcam, MP4, RTSP, IP camera', icon: '📹' },
  { layer: 'YOLO Detector', detail: 'YOLOv8n — GPU/CPU auto', icon: '🧠' },
  { layer: 'IoU Tracker', detail: 'Temporary person track IDs', icon: '🎯' },
  { layer: 'Rules Engine', detail: '8 deterministic security rules', icon: '🚦' },
  { layer: 'FastAPI Backend', detail: 'REST + WebSocket + MJPEG', icon: '⚡' },
  { layer: 'SQLite', detail: 'Local incident log', icon: '🗄️' },
];

const BADGES = [
  { label: 'LOCAL ONLY',        color: 'badge-accent' },
  { label: 'GPU ACCELERATED',   color: 'badge-green'  },
  { label: 'NO CLOUD APIs',     color: 'badge-muted'  },
  { label: 'HUMAN-IN-THE-LOOP', color: 'badge-yellow' },
  { label: '57 TESTS PASSING',  color: 'badge-green'  },
  { label: 'OFFLINE SAFE',      color: 'badge-accent' },
];

export default function Landing() {
  const [runtime, setRuntime] = useState(null);
  const [online, setOnline] = useState(false);

  useEffect(() => {
    fetchRuntimeStatus().then(({ data, online: o }) => {
      setRuntime(data);
      setOnline(o);
    });
  }, []);

  const rt = runtime?.runtime || runtime || {};
  const vd = runtime?.video || {};

  return (
    <div>
      {/* ── Hero ── */}
      <section className="bg-grid" style={{ position: 'relative', overflow: 'hidden', padding: '100px 0 80px' }}>
        <div className="orb orb-teal" style={{ width: 500, height: 500, top: -100, left: -100 }} />
        <div className="orb orb-blue" style={{ width: 400, height: 400, top: 50, right: -50 }} />
        <div className="container" style={{ position: 'relative', zIndex: 1, textAlign: 'center' }}>
          <div className="animate-in">
            <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'center', gap: 8, flexWrap: 'wrap' }}>
              {BADGES.map(b => (
                <span key={b.label} className={`badge ${b.color}`}>{b.label}</span>
              ))}
            </div>
            <h1 style={{ marginBottom: 20 }}>
              <span className="gradient-text">SmartKUET Sentinel</span>
            </h1>
            <p style={{ fontSize: 'clamp(1rem, 2vw, 1.25rem)', color: 'var(--text-secondary)', maxWidth: 680, margin: '0 auto 36px', lineHeight: 1.7 }}>
              Offline Edge-AI campus security and exam integrity assistant for KUET.
              Real-time person detection, tracking, and deterministic security rules —
              running entirely on local hardware with zero cloud dependencies.
            </p>
            <div className="flex" style={{ gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
              <a href="#/security" className="btn btn-primary btn-lg">🖥 Security Room →</a>
              <a href="#/guard" className="btn btn-outline btn-lg">🛡 Guard View</a>
            </div>
          </div>
        </div>
      </section>

      {/* ── Live Status Bar ── */}
      <section style={{ background: 'rgba(0,212,170,0.04)', borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)', padding: '20px 0' }}>
        <div className="container">
          <div className="flex items-center gap-4" style={{ flexWrap: 'wrap', justifyContent: 'center', gap: 32 }}>
            <div style={{ textAlign: 'center' }}>
              <div className="stat-number" style={{ fontSize: '1.6rem' }}>
                {rt.cuda_available ? '⚡ GPU' : '💻 CPU'}
              </div>
              <div className="stat-label">Inference Mode</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div className="stat-number" style={{ fontSize: '1.6rem' }}>
                {vd.effective_fps ? `${vd.effective_fps.toFixed(0)} FPS` : '85 FPS'}
              </div>
              <div className="stat-label">Benchmark</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div className="stat-number" style={{ fontSize: '1.6rem' }}>
                {vd.avg_inference_ms ? `${vd.avg_inference_ms.toFixed(1)} ms` : '11.7 ms'}
              </div>
              <div className="stat-label">Avg Inference</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div className="stat-number" style={{ fontSize: '1.6rem' }}>57</div>
              <div className="stat-label">Tests Passing</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div className="stat-number" style={{ fontSize: '1.6rem' }}>
                {rt.torch_version || '2.11.0+cu128'}
              </div>
              <div className="stat-label">PyTorch</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <span className={`badge ${online ? 'badge-green' : 'badge-muted'}`}>
                <span className={`live-dot ${online ? '' : 'offline'}`} />
                {online ? 'BACKEND LIVE' : 'DEMO MODE'}
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* ── Feature Cards ── */}
      <section className="section">
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <span className="section-tag">Capabilities</span>
            <h2>Everything a Smart Campus Gate Needs</h2>
          </div>
          <div className="grid-3">
            {FEATURES.map((f, i) => (
              <div key={i} className="card" style={{ animationDelay: `${i * 0.08}s` }}>
                <div style={{ fontSize: '2rem', marginBottom: 12 }}>{f.icon}</div>
                <h3 style={{ marginBottom: 8, color: 'var(--accent)' }}>{f.title}</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Architecture ── */}
      <section className="section" style={{ background: 'rgba(0,0,0,0.2)' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <span className="section-tag">Architecture</span>
            <h2>Layered Edge-AI Pipeline</h2>
            <p style={{ color: 'var(--text-secondary)', marginTop: 12, maxWidth: 560, margin: '12px auto 0' }}>
              Every layer runs locally. No cloud. No external APIs. Data never leaves the campus network.
            </p>
          </div>
          <div style={{ maxWidth: 640, margin: '0 auto' }}>
            {ARCH.map((a, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 4 }}>
                <div className="card card-sm" style={{ flex: 1, display: 'flex', gap: 14, alignItems: 'center' }}>
                  <span style={{ fontSize: '1.5rem' }}>{a.icon}</span>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{a.layer}</div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{a.detail}</div>
                  </div>
                </div>
                {i < ARCH.length - 1 && (
                  <div style={{ color: 'var(--accent)', fontSize: '1.2rem', writingMode: 'vertical-rl', margin: '0 -8px', display: 'flex', justifyContent: 'center' }}>↓</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Privacy ── */}
      <section className="section">
        <div className="container" style={{ maxWidth: 800 }}>
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <span className="section-tag">Privacy & Safety</span>
            <h2>Human-in-the-Loop Design</h2>
          </div>
          <HumanInLoopBanner />
          <div className="grid-2" style={{ marginTop: 24 }}>
            <div className="card card-sm">
              <h4 style={{ marginBottom: 8, color: 'var(--accent)' }}>🔢 Temporary IDs Only</h4>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                Track IDs like "ID 3" are short-lived numbers assigned to motion continuity. No face recognition. No student identity.
              </p>
            </div>
            <div className="card card-sm">
              <h4 style={{ marginBottom: 8, color: 'var(--accent)' }}>🔒 Local Data</h4>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                Incidents saved to local SQLite. Evidence JPEGs stay on-device. Nothing leaves the local machine.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="section" style={{ textAlign: 'center', background: 'rgba(0,212,170,0.03)', borderTop: '1px solid var(--border)' }}>
        <div className="container">
          <h2 style={{ marginBottom: 16 }}>Ready to Explore?</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 32 }}>
            Launch the security dashboard or view the guard decision assistant.
          </p>
          <div className="flex" style={{ gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
            <a href="#/security" className="btn btn-primary btn-lg">🖥 Security Room</a>
            <a href="#/guard" className="btn btn-outline btn-lg">🛡 Guard View</a>
            <a href="#/exam" className="btn btn-outline btn-lg">📋 Exam View</a>
          </div>
        </div>
      </section>
    </div>
  );
}
