import { useState, useEffect } from 'react';

const PAGES = ['/', '/security', '/guard', '/exam'];
const LABELS = { '/': 'Home', '/security': 'Security Room', '/guard': 'Guard View', '/exam': 'Exam View' };

export default function NavBar() {
  const [page, setPage] = useState(window.location.hash.replace('#', '') || '/');

  useEffect(() => {
    const onHash = () => setPage(window.location.hash.replace('#', '') || '/');
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  return (
    <nav className="navbar">
      <a className="nav-logo" href="#/">
        <div className="logo-mark">🛡</div>
        <span>SmartKUET <span style={{ color: 'var(--accent)' }}>Sentinel</span></span>
      </a>

      <ul className="nav-links">
        {PAGES.map(p => (
          <li key={p}>
            <a
              href={`#${p}`}
              className={page === p ? 'active' : ''}
            >
              {LABELS[p]}
            </a>
          </li>
        ))}
      </ul>

      <div className="flex items-center gap-2">
        <span className="badge badge-accent">
          <span className="live-dot" />
          OFFLINE-SAFE
        </span>
      </div>
    </nav>
  );
}
