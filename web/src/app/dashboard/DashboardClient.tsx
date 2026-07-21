'use client';

import { useState } from 'react';
import Link from 'next/link';
import styles from './dashboard.module.css';

interface Plan {
  id: string;
  name: string;
  price: number;
  duration: number;
  bandwidth: string;
  features: string[];
}

interface Receipt {
  id: string;
  status: string;
  receiptType: string;
  createdAt?: string;
}

interface Subscription {
  id: string;
  status: string;
  config: string | null;
  expiresAt: string | null;
  createdAt: string;
  plan: Plan;
  receipt: Receipt | null;
}

interface Props {
  subscriptions: Subscription[];
  username: string;
}

const STATUS_MAP: Record<string, { label: string; class: string; icon: string }> = {
  pending:  { label: 'Pending Payment', class: 'orange', icon: '⏳' },
  active:   { label: 'Active',          class: 'green',  icon: '🟢' },
  expired:  { label: 'Expired',         class: 'red',    icon: '🔴' },
  rejected: { label: 'Rejected',        class: 'red',    icon: '❌' },
};

const RECEIPT_STATUS: Record<string, { label: string; class: string }> = {
  pending:  { label: 'Under Review', class: 'orange' },
  approved: { label: 'Approved',     class: 'green' },
  rejected: { label: 'Rejected',     class: 'red' },
};

export function DashboardClient({ subscriptions, username }: Props) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [copied, setCopied] = useState('');

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(id);
      setTimeout(() => setCopied(''), 2000);
    });
  };

  const activeCount = subscriptions.filter((s) => s.status === 'active').length;
  const pendingCount = subscriptions.filter((s) => s.status === 'pending').length;

  const getConfig = (sub: Subscription): { links: string[]; subscriptionUrl?: string } | null => {
    if (!sub.config) return null;
    try { return JSON.parse(sub.config); } catch { return null; }
  };

  return (
    <div className={styles.page}>
      <div className="container">
        {/* Header */}
        <div className={styles.pageHeader}>
          <div>
            <h1 className={styles.pageTitle}>Dashboard</h1>
            <p className={styles.pageSubtitle}>Welcome back, <strong>{username}</strong></p>
          </div>
          <Link href="/vpn" className="btn btn-primary btn-sm">
            + Buy VPN Plan
          </Link>
        </div>

        {/* Stats row */}
        <div className={styles.statsRow}>
          <div className={styles.statCard}>
            <div className={styles.statIcon}>📦</div>
            <div>
              <div className={styles.statNum}>{subscriptions.length}</div>
              <div className={styles.statLabel}>Total Orders</div>
            </div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statIcon}>🟢</div>
            <div>
              <div className={styles.statNum}>{activeCount}</div>
              <div className={styles.statLabel}>Active VPNs</div>
            </div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statIcon}>⏳</div>
            <div>
              <div className={styles.statNum}>{pendingCount}</div>
              <div className={styles.statLabel}>Pending Review</div>
            </div>
          </div>
          <div className={styles.statCard}>
            <div className={styles.statIcon}>💬</div>
            <div className={styles.statNum}>
              <a href="https://t.me/shipien" target="_blank" rel="noopener noreferrer" className={styles.tgLink}>
                @shipien
              </a>
            </div>
            <div className={styles.statLabel}>Support</div>
          </div>
        </div>

        {/* Subscriptions */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>My VPN Subscriptions</h2>

          {subscriptions.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>🔒</div>
              <p>No VPN subscriptions yet.</p>
              <Link href="/vpn" className="btn btn-primary" style={{ marginTop: '16px' }}>
                Browse Plans
              </Link>
            </div>
          ) : (
            <div className={styles.subList}>
              {subscriptions.map((sub) => {
                const st = STATUS_MAP[sub.status] || STATUS_MAP.pending;
                const config = getConfig(sub);
                const isExpanded = expandedId === sub.id;
                const receiptSt = sub.receipt ? RECEIPT_STATUS[sub.receipt.status] : null;
                const expDate = sub.expiresAt ? new Date(sub.expiresAt) : null;
                const isExpired = expDate ? expDate < new Date() : false;

                return (
                  <div key={sub.id} className={styles.subCard}>
                    <div className={styles.subHeader} onClick={() => setExpandedId(isExpanded ? null : sub.id)}>
                      <div className={styles.subLeft}>
                        <div className={styles.subIcon}>{st.icon}</div>
                        <div>
                          <div className={styles.subPlanName}>{sub.plan.name}</div>
                          <div className={styles.subMeta}>
                            {sub.plan.bandwidth} · {sub.plan.duration} days ·{' '}
                            <span className={styles.subDate}>
                              {new Date(sub.createdAt).toLocaleDateString('en-GB')}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className={styles.subRight}>
                        <span className={`badge badge-${st.class === 'green' ? 'green' : st.class === 'orange' ? 'orange' : 'red'}`}>
                          {st.label}
                        </span>
                        <span className={styles.expandArrow}>{isExpanded ? '▲' : '▼'}</span>
                      </div>
                    </div>

                    {isExpanded && (
                      <div className={styles.subBody}>
                        <div className="divider" />

                        {/* Expiry */}
                        {expDate && (
                          <div className={styles.infoRow}>
                            <span className={styles.infoLabel}>Expires</span>
                            <span className={`${styles.infoVal} ${isExpired ? styles.expired : ''}`}>
                              {isExpired ? '⚠️ ' : ''}
                              {expDate.toLocaleDateString('en-GB', { year: 'numeric', month: 'short', day: 'numeric' })}
                            </span>
                          </div>
                        )}

                        {/* Receipt status */}
                        {receiptSt && (
                          <div className={styles.infoRow}>
                            <span className={styles.infoLabel}>Payment Receipt</span>
                            <span className={`badge badge-${receiptSt.class === 'green' ? 'green' : receiptSt.class === 'orange' ? 'orange' : 'red'}`} style={{ fontSize: '11px' }}>
                              {receiptSt.label}
                            </span>
                          </div>
                        )}

                        {/* No receipt uploaded yet */}
                        {sub.status === 'pending' && !sub.receipt && (
                          <div className={styles.uploadReminder}>
                            ⚠️ You haven&apos;t uploaded a payment receipt yet.{' '}
                            <Link href="/vpn" className={styles.inlineLink}>Go to VPN page</Link> and upload your receipt.
                          </div>
                        )}

                        {/* VPN Config */}
                        {sub.status === 'active' && config && (
                          <div className={styles.configSection}>
                            <p className={styles.configTitle}>🔑 Your VPN Configurations</p>
                            {config.links && config.links.length > 0 ? (
                              <div className={styles.configList}>
                                {config.links.slice(0, 3).map((link, i) => {
                                  const clientName = config.clientName;
                                  const baseSubUrl = clientName 
                                    ? `http://h2.morningislighting.ir:2096/sub/${clientName}`
                                    : (typeof window !== 'undefined' ? `${window.location.origin}/api/vpn/config/sub/${sub.id}` : '');
                                  
                                  const jsonSubUrl = clientName 
                                    ? `http://h2.morningislighting.ir:2096/sub/${clientName}?format=json`
                                    : (typeof window !== 'undefined' ? `${window.location.origin}/api/vpn/config/${sub.id}` : '');

                                  const clashSubUrl = clientName
                                    ? `http://h2.morningislighting.ir:2096/sub/${clientName}?format=clash`
                                    : '';
                                    
                                  const downloadJsonUrl = clientName
                                    ? `http://h2.morningislighting.ir:2096/sub/${clientName}?format=json`
                                    : (typeof window !== 'undefined' ? `${window.location.origin}/api/vpn/config/json/${sub.id}` : '');

                                  return (
                                    <div key={i} className={styles.configWrap}>
                                      {/* anytls Link */}
                                      <div className={styles.configGroup}>
                                        <span className={styles.configLabel}>anytls Configuration Link</span>
                                        <div className={styles.configItem}>
                                          <code className={styles.configCode}>
                                            {link.slice(0, 45)}...
                                          </code>
                                          <button
                                            className="btn btn-outline btn-sm"
                                            onClick={() => copyToClipboard(link, `${sub.id}-${i}-anytls`)}
                                          >
                                            {copied === `${sub.id}-${i}-anytls` ? '✓ Copied' : 'Copy'}
                                          </button>
                                        </div>
                                      </div>

                                      {/* Base64 Subscription Link */}
                                      <div className={styles.configGroup} style={{ marginTop: '8px' }}>
                                        <span className={styles.configLabel}>Karing / V2Ray Base64 Subscription Link</span>
                                        <div className={styles.configItem}>
                                          <code className={styles.configCode}>
                                            {baseSubUrl.slice(0, 45)}...
                                          </code>
                                          <button
                                            className="btn btn-outline btn-sm"
                                            onClick={() => copyToClipboard(baseSubUrl, `${sub.id}-${i}-b64`)}
                                          >
                                            {copied === `${sub.id}-${i}-b64` ? '✓ Copied' : 'Copy'}
                                          </button>
                                        </div>
                                      </div>

                                      {/* JSON Subscription Link */}
                                      <div className={styles.configGroup} style={{ marginTop: '8px' }}>
                                        <span className={styles.configLabel}>sing-box JSON Subscription Link</span>
                                        <div className={styles.configItem}>
                                          <code className={styles.configCode}>
                                            {jsonSubUrl.slice(0, 45)}...
                                          </code>
                                          <button
                                            className="btn btn-outline btn-sm"
                                            onClick={() => copyToClipboard(jsonSubUrl, `${sub.id}-${i}-json`)}
                                          >
                                            {copied === `${sub.id}-${i}-json` ? '✓ Copied' : 'Copy'}
                                          </button>
                                        </div>
                                      </div>

                                      {/* Clash Subscription Link */}
                                      {clashSubUrl && (
                                        <div className={styles.configGroup} style={{ marginTop: '8px' }}>
                                          <span className={styles.configLabel}>Clash Subscription Link</span>
                                          <div className={styles.configItem}>
                                            <code className={styles.configCode}>
                                              {clashSubUrl.slice(0, 45)}...
                                            </code>
                                            <button
                                              className="btn btn-outline btn-sm"
                                              onClick={() => copyToClipboard(clashSubUrl, `${sub.id}-${i}-clash`)}
                                            >
                                              {copied === `${sub.id}-${i}-clash` ? '✓ Copied' : 'Copy'}
                                            </button>
                                          </div>
                                        </div>
                                      )}

                                      {/* Download JSON File */}
                                      <div className={styles.configGroup} style={{ marginTop: '8px' }}>
                                        <span className={styles.configLabel}>JSON File Configuration</span>
                                        <div className={styles.configItem}>
                                          <code className={styles.configCode}>
                                            {clientName ? `${clientName}.json` : 'shipien-config.json'}
                                          </code>
                                          <a
                                            href={downloadJsonUrl}
                                            className="btn btn-outline btn-sm"
                                            style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', justifyContent: 'center' }}
                                          >
                                            Download JSON
                                          </a>
                                        </div>
                                      </div>

                                      {/* sing-box QR Code */}
                                      {jsonSubUrl && (
                                        <div className={styles.qrContainer} style={{ marginTop: '12px' }}>
                                          <p className={styles.qrLabel}>📱 Scan in sing-box app (imports JSON config):</p>
                                          <div className={styles.qrBg}>
                                            <img 
                                              src={`https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=${encodeURIComponent(jsonSubUrl)}`}
                                              alt="sing-box JSON Config QR Code"
                                              width={160}
                                              height={160}
                                              loading="lazy"
                                            />
                                          </div>
                                        </div>
                                      )}
                                    </div>
                                  );
                                })}
                              </div>
                            ) : (
                              <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                                Config will appear here. Contact support if it&apos;s taking too long.
                              </p>
                            )}

                            <div className={styles.guideLinks}>
                              <p className={styles.configTitle}>📚 Setup Guide for sing-box (anytls)</p>
                              <div className={styles.guideGrid}>
                                <div className={styles.guideItem}>
                                  <strong>📱 Android</strong>
                                  <span style={{ marginBottom: '8px' }}>Install sing-box client:</span>
                                  <a href="https://play.google.com/store/apps/details?id=io.nekohasekai.singbox" target="_blank" rel="noopener noreferrer" className="btn btn-outline btn-sm" style={{ fontSize: '11px', padding: '6px 10px', marginBottom: '6px' }}>Play Store</a>
                                  <a href="https://github.com/SagerNet/sing-box/releases" target="_blank" rel="noopener noreferrer" className="btn btn-ghost btn-sm" style={{ fontSize: '11px', padding: '4px' }}>Direct APK (Github)</a>
                                  <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '6px' }}>Copy config, open sing-box ➔ Profiles ➔ Import Profile ➔ Paste and Connect.</span>
                                </div>
                                <div className={styles.guideItem}>
                                  <strong>🍏 iOS (iPhone)</strong>
                                  <span style={{ marginBottom: '8px' }}>Install Karing client:</span>
                                  <a href="https://apps.apple.com/us/app/karing/id6472431552" target="_blank" rel="noopener noreferrer" className="btn btn-outline btn-sm" style={{ fontSize: '11px', padding: '6px 10px', marginBottom: '8px' }}>App Store (Karing)</a>
                                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Scan the QR Code directly from the Karing app or click "Copy JSON Link" and import it under "Profiles".</span>
                                </div>
                                <div className={styles.guideItem}>
                                  <strong>💻 Desktop (PC / Mac)</strong>
                                  <span style={{ marginBottom: '8px' }}>Install client:</span>
                                  <a href="https://github.com/SagerNet/sing-box/releases" target="_blank" rel="noopener noreferrer" className="btn btn-outline btn-sm" style={{ fontSize: '11px', padding: '6px 10px', marginBottom: '8px' }}>Download Client</a>
                                  <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Load anytls config profile via dashboard interface.</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Rejected */}
                        {sub.status === 'rejected' && (
                          <div className={styles.rejectedNote}>
                            ❌ Your payment was not approved. Please contact{' '}
                            <a href="https://t.me/shipien" target="_blank" rel="noopener noreferrer" className={styles.inlineLink}>
                              @shipien on Telegram
                            </a>{' '}
                            for assistance.
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Help */}
        <div className={styles.helpBox}>
          <div className={styles.helpIcon}>💬</div>
          <div>
            <p className={styles.helpTitle}>Need Help?</p>
            <p className={styles.helpText}>Contact our support team directly on Telegram for fast assistance.</p>
          </div>
          <a
            href="https://t.me/shipien"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-outline btn-sm"
          >
            Message @shipien
          </a>
        </div>
      </div>
    </div>
  );
}
