'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import styles from '../auth.module.css';

export default function SignupPage() {
  const router = useRouter();
  const [form, setForm] = useState({ username: '', phone: '', password: '', confirm: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (form.password !== form.confirm) { setError('Passwords do not match'); return; }
    if (form.password.length < 6) { setError('Password must be at least 6 characters'); return; }
    setLoading(true);
    try {
      const res = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: form.username, phone: form.phone, password: form.password }),
      });
      const data = await res.json();
      if (!res.ok) { setError(data.error || 'Signup failed'); return; }
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
          <div className={styles.iconBadge}>🚀</div>
          <h1 className={styles.title}>Create account</h1>
          <p className={styles.subtitle}>Join Shipien and unlock all services</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {error && <div className={styles.errorBanner}>{error}</div>}

          <div className="input-group">
            <label className="input-label" htmlFor="username">Username</label>
            <input
              id="username"
              className="input"
              type="text"
              placeholder="choose_a_username"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
              minLength={3}
              maxLength={32}
              pattern="[a-zA-Z0-9_]+"
              title="Only letters, numbers and underscores"
              autoComplete="username"
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="phone">Phone Number</label>
            <input
              id="phone"
              className="input"
              type="tel"
              placeholder="+98 912 000 0000"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              required
              autoComplete="tel"
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
              minLength={6}
              autoComplete="new-password"
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="confirm">Confirm Password</label>
            <input
              id="confirm"
              className="input"
              type="password"
              placeholder="••••••••"
              value={form.confirm}
              onChange={(e) => setForm({ ...form, confirm: e.target.value })}
              required
              autoComplete="new-password"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-full"
            disabled={loading}
            style={{ marginTop: '8px', padding: '14px' }}
          >
            {loading ? (
              <><span className={styles.spinner} /> Creating account...</>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        <div className={styles.cardFooter}>
          <p>
            Already have an account?{' '}
            <Link href="/auth/login" className={styles.link}>Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
