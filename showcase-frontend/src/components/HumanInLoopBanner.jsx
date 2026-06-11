export default function HumanInLoopBanner({ message }) {
  return (
    <div className="hitl-banner">
      <span style={{ fontSize: '1.2rem' }}>⚠️</span>
      <div>
        <strong>Human-in-the-Loop:</strong>{' '}
        {message || 'All automated alerts are advisory only. Final gate control decisions are made exclusively by the human security guard.'}
      </div>
    </div>
  );
}
