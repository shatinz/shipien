import Link from 'next/link';

export default function NotFound() {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '16px',
      padding: '40px',
      textAlign: 'center',
    }}>
      <div style={{ fontSize: '80px' }}>404</div>
      <h1 style={{ fontSize: '28px', fontWeight: '800', letterSpacing: '-0.03em' }}>
        Page not found
      </h1>
      <p style={{ color: 'var(--text-secondary)', fontSize: '16px' }}>
        The page you&apos;re looking for doesn&apos;t exist or has been moved.
      </p>
      <Link href="/" className="btn btn-primary" style={{ marginTop: '8px' }}>
        Back to Home
      </Link>
    </div>
  );
}
