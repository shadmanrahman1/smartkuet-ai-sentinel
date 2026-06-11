import HumanInLoopBanner from '../components/HumanInLoopBanner';

const MOCK_STUDENTS = [
  { id: 'ECE-4201', seat: 'A-01', status: 'normal',    score: 12, flag: '✅', note: 'Focused' },
  { id: 'CSE-4187', seat: 'A-02', status: 'normal',    score: 8,  flag: '✅', note: 'Focused' },
  { id: 'ME-4154',  seat: 'B-01', status: 'low',       score: 34, flag: '⚠️', note: 'Head movement' },
  { id: 'EEE-4099', seat: 'B-02', status: 'moderate',  score: 51, flag: '🟠', note: 'Phone detected' },
  { id: 'CE-4212',  seat: 'C-01', status: 'normal',    score: 5,  flag: '✅', note: 'Focused' },
  { id: 'IPE-4177', seat: 'C-02', status: 'high',      score: 78, flag: '🚨', note: 'Repeated movement + phone' },
];

const STATUS_COLORS = {
  normal:   { color: 'var(--green)',  bg: 'var(--green-bg)',  label: 'Normal' },
  low:      { color: 'var(--yellow)', bg: 'var(--yellow-bg)', label: 'Low' },
  moderate: { color: 'var(--orange)', bg: 'var(--orange-bg)', label: 'Moderate' },
  high:     { color: 'var(--red)',    bg: 'var(--red-bg)',    label: 'High' },
};

const FUTURE_MODULES = [
  {
    icon: '👁️',
    title: 'Gaze Direction Analysis',
    desc: 'Detect when a student repeatedly looks off-screen or at another paper.',
    status: 'Planned',
  },
  {
    icon: '📱',
    title: 'Phone Detection',
    desc: 'Real-time YOLO detection of mobile phones on desks or in hand.',
    status: 'Partially Active',
  },
  {
    icon: '📋',
    title: 'Behavioral Scoring',
    desc: 'Aggregate suspicion score from head movement, phone, and gaze signals.',
    status: 'Mock / Concept',
  },
  {
    icon: '🧑‍🏫',
    title: 'Examiner Override',
    desc: 'Examiner can dismiss or escalate any flagged event with a single click.',
    status: 'Concept',
  },
];

export default function ExamView() {
  const high = MOCK_STUDENTS.filter(s => s.status === 'high' || s.status === 'moderate');

  return (
    <div className="section">
      <div className="container">
        {/* ── Header ── */}
        <div style={{ marginBottom: 32 }}>
          <span className="section-tag">Examiner / Invigilation View</span>
          <div className="flex items-center justify-between" style={{ flexWrap: 'wrap', gap: 12 }}>
            <h2>📋 Exam Integrity Monitor</h2>
            <span className="badge badge-muted">CONCEPT / FUTURE MODULE</span>
          </div>
          <p style={{ color: 'var(--text-secondary)', marginTop: 8, fontSize: '0.9rem', maxWidth: 700 }}>
            This page demonstrates the planned examiner invigilation concept.
            Suspicion scores are mock data — real cheating detection is a planned future milestone.
          </p>
        </div>

        {/* ── Alert banner for flagged students ── */}
        {high.length > 0 && (
          <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 12, padding: '16px 20px', marginBottom: 24, display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: '1.4rem' }}>🚨</span>
            <div>
              <div style={{ fontWeight: 700, color: 'var(--red)', marginBottom: 4 }}>
                {high.length} student{high.length > 1 ? 's' : ''} flagged for review
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                {high.map(s => s.id).join(', ')} — examiner attention required
              </div>
            </div>
          </div>
        )}

        {/* ── Student Cards ── */}
        <div style={{ marginBottom: 32 }}>
          <h3 style={{ marginBottom: 16 }}>🪑 Exam Hall Overview</h3>
          <div className="grid-3">
            {MOCK_STUDENTS.map(s => {
              const st = STATUS_COLORS[s.status];
              return (
                <div key={s.id} className="card" style={{ border: `1px solid ${st.color}40`, background: `linear-gradient(135deg, ${st.bg}, var(--bg-card))` }}>
                  <div className="flex items-center justify-between" style={{ marginBottom: 12 }}>
                    <div>
                      <div className="mono" style={{ fontWeight: 700, color: 'var(--accent)', fontSize: '0.95rem' }}>{s.id}</div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Seat {s.seat}</div>
                    </div>
                    <span style={{ fontSize: '1.5rem' }}>{s.flag}</span>
                  </div>

                  <div style={{ marginBottom: 12 }}>
                    <div className="flex items-center justify-between" style={{ marginBottom: 6 }}>
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Suspicion Score</span>
                      <span style={{ fontWeight: 800, color: st.color }}>{s.score}%</span>
                    </div>
                    <div style={{ height: 6, background: 'rgba(255,255,255,0.08)', borderRadius: 3, overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${s.score}%`, background: st.color, borderRadius: 3, transition: 'width 0.5s ease' }} />
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{s.note}</span>
                    <span className="badge" style={{ color: st.color, background: st.bg, borderColor: `${st.color}40`, fontSize: '0.7rem' }}>
                      {st.label}
                    </span>
                  </div>

                  {(s.status === 'high' || s.status === 'moderate') && (
                    <div className="flex gap-2" style={{ marginTop: 12 }}>
                      <button className="btn btn-outline" style={{ flex: 1, justifyContent: 'center', fontSize: '0.78rem', padding: '6px 10px' }}>
                        ✅ Dismiss
                      </button>
                      <button className="btn" style={{ flex: 1, justifyContent: 'center', fontSize: '0.78rem', padding: '6px 10px', background: 'var(--red)', color: '#fff' }}>
                        🚨 Escalate
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* ── Stats summary ── */}
        <div className="grid-4" style={{ marginBottom: 32 }}>
          {[
            { label: 'Total Seated', val: MOCK_STUDENTS.length, color: 'var(--accent)' },
            { label: 'Normal', val: MOCK_STUDENTS.filter(s => s.status === 'normal').length, color: 'var(--green)' },
            { label: 'Flagged', val: MOCK_STUDENTS.filter(s => s.status !== 'normal').length, color: 'var(--yellow)' },
            { label: 'High Priority', val: MOCK_STUDENTS.filter(s => s.status === 'high').length, color: 'var(--red)' },
          ].map(item => (
            <div key={item.label} className="card card-sm" style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 900, color: item.color }}>{item.val}</div>
              <div className="stat-label">{item.label}</div>
            </div>
          ))}
        </div>

        {/* ── Future Modules ── */}
        <div style={{ marginBottom: 32 }}>
          <h3 style={{ marginBottom: 6 }}>🔭 Planned Detection Modules</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: 20 }}>
            The SmartKUET vision includes these future AI modules. Current implementation uses YOLO phone detection only.
          </p>
          <div className="grid-2">
            {FUTURE_MODULES.map((m, i) => (
              <div key={i} className="card card-sm flex gap-4 items-center">
                <span style={{ fontSize: '2rem' }}>{m.icon}</span>
                <div>
                  <div className="flex items-center gap-2" style={{ marginBottom: 4 }}>
                    <h4>{m.title}</h4>
                    <span className="badge badge-muted" style={{ fontSize: '0.65rem' }}>{m.status}</span>
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{m.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <HumanInLoopBanner message="Examiner review and intervention is required for all flagged events. No automated actions are taken without human approval." />
      </div>
    </div>
  );
}
