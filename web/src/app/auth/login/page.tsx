'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import styles from '../auth.module.css';

export default function LoginPage() {
  const router = useRouter();
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) { setError(data.error || 'Login failed'); return; }
      router.push('/dashboard');
      router.refresh();
    } catch {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.glow} />
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <div className={styles.iconBadge}>🔐</div>
          <h1 className={styles.title}>Welcome back</h1>
          <p className={styles.subtitle}>Sign in to your Shipien account</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {error && <div className={styles.errorBanner}>{error}</div>}

          <div className="input-group">
            <label className="input-label" htmlFor="username">Username</label>
            <input
              id="username"
              className="input"
              type="text"
              placeholder="your_username"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
              autoComplete="username"
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="password">Password</label>
            <input
              id="password"
              className="input"
              type="password"
              placeholder="••••••••"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
              autoComplete="current-password"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-full"
            disabled={loading}
            style={{ marginTop: '8px', padding: '14px' }}
          >
            {loading ? (
              <><span className={styles.spinner} /> Signing in...</>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <div className={styles.cardFooter}>
          <p>
            Don&apos;t have an account?{' '}
            <Link href="/auth/signup" className={styles.link}>Create one</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
