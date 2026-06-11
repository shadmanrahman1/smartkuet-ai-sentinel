import { useState, useEffect } from 'react';
import NavBar from './components/NavBar';
import Landing from './pages/Landing';
import SecurityRoom from './pages/SecurityRoom';
import GuardView from './pages/GuardView';
import ExamView from './pages/ExamView';

function getPage() {
  return window.location.hash.replace('#', '') || '/';
}

export default function App() {
  const [page, setPage] = useState(getPage);

  useEffect(() => {
    const onHash = () => setPage(getPage());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  const renderPage = () => {
    switch (page) {
      case '/security': return <SecurityRoom />;
      case '/guard':    return <GuardView />;
      case '/exam':     return <ExamView />;
      default:          return <Landing />;
    }
  };

  return (
    <>
      <NavBar />
      <main>{renderPage()}</main>
      <footer style={{
        borderTop: '1px solid var(--border)',
        padding: '20px 32px',
        textAlign: 'center',
        fontSize: '0.78rem',
        color: 'var(--text-muted)',
        background: 'rgba(0,0,0,0.2)',
      }}>
        SmartKUET Sentinel — Offline Edge-AI Campus Security &nbsp;·&nbsp;
        KUET Innovation Project &nbsp;·&nbsp;
        <span style={{ color: 'var(--accent)' }}>Local deployment only · No cloud APIs</span>
      </footer>
    </>
  );
}
