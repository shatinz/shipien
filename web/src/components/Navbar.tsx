'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import styles from './Navbar.module.css';

export function Navbar() {
  const [user, setUser] = useState<{ username: string } | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    fetch('/api/auth/me')
      .then((r) => r.json())
      .then((d) => setUser(d.user))
      .catch(() => {});
  }, [pathname]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST' });
    setUser(null);
    router.push('/');
    router.refresh();
  };

  const navLinks = [
    { href: '/', label: 'Home' },
    { href: '/services', label: 'Services' },
    ...(user ? [{ href: '/vpn', label: 'VPN' }] : []),
    ...(user ? [{ href: '/dashboard', label: 'Dashboard' }] : []),
  ];

  return (
    <header className={`${styles.header} ${scrolled ? styles.scrolled : ''}`}>
      <div className={`container ${styles.nav}`}>
        {/* Logo */}
        <Link href="/" className={styles.logo}>
          <div className={styles.logoIcon}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <span>Shipien</span>
        </Link>

        {/* Desktop Nav */}
        <nav className={styles.desktopNav}>
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`${styles.navLink} ${pathname === link.href ? styles.active : ''}`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Auth */}
        <div className={styles.authArea}>
          {user ? (
            <div className={styles.userMenu}>
              <span className={styles.username}>
                <div className={styles.avatarDot} />
                {user.username}
              </span>
              <button className="btn btn-outline btn-sm" onClick={handleLogout}>
                Logout
              </button>
            </div>
          ) : (
            <div className={styles.authButtons}>
              <Link href="/auth/login" className="btn btn-ghost btn-sm">Login</Link>
              <Link href="/auth/signup" className="btn btn-primary btn-sm">Sign Up</Link>
            </div>
          )}

          {/* Mobile hamburger */}
          <button
            className={styles.hamburger}
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Menu"
          >
            <span className={menuOpen ? styles.barOpen : ''} />
            <span className={menuOpen ? styles.barOpen : ''} />
            <span className={menuOpen ? styles.barOpen : ''} />
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className={styles.mobileMenu}>
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={styles.mobileLink}
              onClick={() => setMenuOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          <div className={styles.mobileDivider} />
          {user ? (
            <button className="btn btn-outline btn-sm btn-full" onClick={handleLogout}>
              Logout
            </button>
          ) : (
            <>
              <Link href="/auth/login" className="btn btn-ghost btn-sm btn-full" onClick={() => setMenuOpen(false)}>Login</Link>
              <Link href="/auth/signup" className="btn btn-primary btn-sm btn-full" onClick={() => setMenuOpen(false)}>Sign Up</Link>
            </>
          )}
        </div>
      )}
    </header>
  );
}
