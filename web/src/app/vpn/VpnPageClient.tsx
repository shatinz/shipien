'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from './vpn.module.css';

interface Plan {
  id: string;
  name: string;
  price: number;
  duration: number;
  bandwidth: string;
  description: string;
  features: string[];
}

interface Props {
  plans: Plan[];
  username: string;
}

const CARD_NUMBER = process.env.NEXT_PUBLIC_CARD_NUMBER || '6037 9981 7457 8640';

export function VpnPageClient({ plans, username }: Props) {
  const router = useRouter();
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null);
  const [step, setStep] = useState<'plans' | 'checkout' | 'done'>('plans');
  const [subscriptionId, setSubscriptionId] = useState('');
  const [receipt, setReceipt] = useState('');
  const [receiptFile, setReceiptFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [configName, setConfigName] = useState('');

  const handleSelectPlan = async (plan: Plan) => {
    setSelectedPlan(plan);
    setLoading(true);
    setError('');
    try {
      const res = await fetch('/api/vpn/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ planId: plan.id }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      setSubscriptionId(data.subscription.id);
      setStep('checkout');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Error creating subscription');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setReceiptFile(file);
    const reader = new FileReader();
    reader.onload = (ev) => setReceipt(ev.target?.result as string);
    reader.readAsDataURL(file);
  };

  const handleUploadReceipt = async (e: React.FormEvent) => {
    e.preventDefault();
    const isFree = selectedPlan?.price === 0;
    if (!isFree && !receipt && !receiptFile) { setError('Please provide a receipt'); return; }
    
    if (configName) {
      if (!/^[a-zA-Z0-9]{3,15}$/.test(configName)) {
        setError('Configuration name must be between 3 and 15 alphanumeric characters (only letters and numbers)');
        return;
      }
    }
    
    setLoading(true);
    setError('');
    try {
      const res = await fetch('/api/payment/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subscriptionId,
          receiptData: isFree ? 'Free Trial Claim' : receipt,
          receiptType: isFree ? 'text' : (receiptFile ? 'image' : 'text'),
          configName: configName || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      setStep('done');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (p: number) =>
    p === 0 ? 'رایگان' : p.toLocaleString('fa-IR') + ' تومان';

  if (step === 'done') {
    return (
      <div className={styles.page}>
        <div className="container">
          <div className={styles.doneCard}>
            <div className={styles.doneIcon}>✅</div>
            <h1>{selectedPlan?.price === 0 ? 'Trial Claimed!' : 'Receipt Submitted!'}</h1>
            <p>
              {selectedPlan?.price === 0 
                ? 'Your free trial activation request has been sent to our admin. We will activate it shortly.' 
                : 'Your payment receipt has been sent to our admin for review. We\'ll activate your VPN shortly.'}
            </p>
            <p className={styles.doneNote}>
              📩 Check your dashboard for status updates. You can also message us on{' '}
              <a href="https://t.me/shipien" target="_blank" rel="noopener noreferrer">Telegram @shipien</a>
            </p>
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', justifyContent: 'center', marginTop: '24px' }}>
              <button className="btn btn-primary" onClick={() => router.push('/dashboard')}>
                Go to Dashboard
              </button>
              <button className="btn btn-outline" onClick={() => { setStep('plans'); setSelectedPlan(null); setSubscriptionId(''); setReceipt(''); setReceiptFile(null); }}>
                Buy Another Plan
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'checkout' && selectedPlan) {
    const isFree = selectedPlan.price === 0;

    return (
      <div className={styles.page}>
        <div className="container">
          <div className={styles.checkoutWrap}>
            <button className="btn btn-ghost btn-sm" onClick={() => { setStep('plans'); setSubscriptionId(''); }} style={{ marginBottom: '24px' }}>
              ← Back to Plans
            </button>

            <div className={styles.checkoutGrid}>
              {/* Order Summary */}
              <div className={styles.orderSummary}>
                <h2 className={styles.checkoutTitle}>Order Summary</h2>
                <div className="card">
                  <div className={styles.orderPlan}>
                    <span className={styles.orderPlanName}>{selectedPlan.name}</span>
                    <span className={styles.orderPrice}>{formatPrice(selectedPlan.price)}</span>
                  </div>
                  <div className="divider" />
                  <ul className={styles.orderFeatures}>
                    {selectedPlan.features.map((f) => (
                      <li key={f}><span>✓</span> {f}</li>
                    ))}
                  </ul>
                  <div className="divider" />
                  <div className={styles.paymentInfo}>
                    {isFree ? (
                      <div>
                        <p className={styles.payLabel}>🎁 Free Trial Activation</p>
                        <p className={styles.payNote}>No payment is required for this trial. Click the button on the right to claim your trial instantly.</p>
                      </div>
                    ) : (
                      <div>
                        <p className={styles.payLabel}>💳 Payment via Card Transfer</p>
                        <div className={styles.cardNumber}>
                          <span>{CARD_NUMBER}</span>
                          <button
                            className="btn btn-outline btn-sm"
                            onClick={() => navigator.clipboard.writeText(CARD_NUMBER)}
                          >
                            Copy
                          </button>
                        </div>
                        <p className={styles.payNote}>Transfer exactly <strong>{formatPrice(selectedPlan.price)}</strong> and upload your receipt below.</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Receipt Upload / Claim Button */}
              <div>
                <h2 className={styles.checkoutTitle}>{isFree ? 'Claim Plan' : 'Upload Receipt'}</h2>
                <div className="card">
                  <form onSubmit={handleUploadReceipt} className={styles.receiptForm}>
                    {error && <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)', borderRadius: '8px', padding: '10px 14px', fontSize: '13px', color: '#fca5a5' }}>{error}</div>}

                    {isFree ? (
                      <div style={{ padding: '24px 0', textAlign: 'center' }}>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', fontSize: '14px', lineHeight: '1.6' }}>
                          Once you click the button below, a request will be sent to the Telegram bot to activate your free trial configuration link.
                        </p>
                        <button
                          type="submit"
                          className="btn btn-primary btn-lg btn-full"
                          disabled={loading}
                        >
                          {loading ? 'Claiming...' : '🎉 Claim Free Trial'}
                        </button>
                      </div>
                    ) : (
                      <>
                        <div className={styles.uploadArea}>
                          <input
                            type="file"
                            id="receipt-file"
                            accept="image/*"
                            onChange={handleFileChange}
                            className={styles.fileInput}
                          />
                          <label htmlFor="receipt-file" className={styles.uploadLabel}>
                            {receiptFile ? (
                              <>
                                <span style={{ fontSize: '24px' }}>🖼️</span>
                                <span className={styles.uploadText}>{receiptFile.name}</span>
                                <span className={styles.uploadSub}>Click to change</span>
                              </>
                            ) : (
                              <>
                                <span style={{ fontSize: '32px' }}>📷</span>
                                <span className={styles.uploadText}>Upload Receipt Photo</span>
                                <span className={styles.uploadSub}>Click or drag & drop an image</span>
                              </>
                            )}
                          </label>
                        </div>

                        <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px', margin: '4px 0' }}>or describe your payment</div>

                        <div className="input-group">
                          <label className="input-label" htmlFor="receipt-text">Payment Description</label>
                          <textarea
                            id="receipt-text"
                            className="input"
                            rows={3}
                            placeholder="e.g. Transferred 150,000 Tomans at 14:30 from account ending in 1234..."
                            value={receiptFile ? '' : receipt}
                            onChange={(e) => { if (!receiptFile) setReceipt(e.target.value); }}
                            disabled={!!receiptFile}
                            style={{ resize: 'vertical', minHeight: '80px' }}
                          />
                        </div>

                        <div className="input-group" style={{ marginTop: '12px' }}>
                          <label className="input-label" htmlFor="config-name">Desired Configuration Name (Optional)</label>
                          <input
                            type="text"
                            id="config-name"
                            className="input"
                            placeholder="e.g. reza123 (3-15 alphanumeric characters)"
                            value={configName}
                            onChange={(e) => setConfigName(e.target.value.toLowerCase().replace(/[^a-z0-9]/g, ''))}
                            maxLength={15}
                            style={{ textTransform: 'lowercase' }}
                          />
                        </div>

                        <button
                          type="submit"
                          className="btn btn-primary btn-full"
                          disabled={loading || (!receipt && !receiptFile)}
                          style={{ padding: '14px' }}
                        >
                          {loading ? 'Submitting...' : '📤 Submit Receipt for Review'}
                        </button>
                      </>
                    )}

                    <p className={styles.contactNote}>
                      Questions? Message us on{' '}
                      <a href="https://t.me/shipien" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-light)' }}>
                        Telegram @shipien
                      </a>
                    </p>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  return (
    <div className={styles.page}>
      <div className={styles.heroGlow} />
      <div className="container">
        <div className={styles.header}>
          <div className="badge badge-accent" style={{ marginBottom: '16px' }}>
            <span className="glow-dot" /> Secure & Fast
          </div>
          <h1 className={styles.title}>VPN Plans</h1>
          <p className={styles.subtitle}>
            High-performance VPN with VLESS, VMess, Trojan & Hysteria2. Choose the plan that fits your needs.
          </p>
          <p className={styles.greeting}>Welcome, <strong>{username}</strong> 👋</p>
        </div>

        {error && <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)', borderRadius: '8px', padding: '12px 16px', marginBottom: '24px', color: '#fca5a5' }}>{error}</div>}

        {plans.length === 0 ? (
          <div className={styles.emptyState}>
            <p>No VPN plans available right now. Check back soon!</p>
            <a href="https://t.me/shipien" target="_blank" rel="noopener noreferrer" className="btn btn-outline" style={{ marginTop: '16px' }}>Contact on Telegram</a>
          </div>
        ) : (
          <div className={styles.plansGrid}>
            {plans.map((plan, i) => (
              <div
                key={plan.id}
                className={`${styles.planCard} ${i === 2 ? styles.featured : ''}`}
              >
                {i === 2 && <div className={styles.featuredBadge}>⭐ Most Popular</div>}
                <div className={styles.planHeader}>
                  <h2 className={styles.planName}>{plan.name}</h2>
                  <div className={styles.planPrice}>
                    <span className={styles.priceAmount}>{plan.price.toLocaleString()}</span>
                    <span className={styles.priceCurrency}>تومان</span>
                  </div>
                  <p className={styles.planDesc}>{plan.description}</p>
                </div>

                <div className={styles.planMeta}>
                  <div className={styles.metaItem}>
                    <span>⏱</span> {plan.duration} days
                  </div>
                  <div className={styles.metaItem}>
                    <span>📡</span> {plan.bandwidth}
                  </div>
                </div>

                <ul className={styles.featureList}>
                  {plan.features.map((f) => (
                    <li key={f}><span className={styles.checkIcon}>✓</span> {f}</li>
                  ))}
                </ul>

                <button
                  className={`btn btn-full ${i === 2 ? 'btn-primary' : 'btn-outline'}`}
                  onClick={() => handleSelectPlan(plan)}
                  disabled={loading}
                  style={{ padding: '13px' }}
                >
                  {loading && selectedPlan?.id === plan.id ? 'Processing...' : 'Get This Plan'}
                </button>
              </div>
            ))}
          </div>
        )}

        <div className={styles.contactBox}>
          <p>Need a custom plan or have questions?</p>
          <a
            href="https://t.me/shipien"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-outline btn-sm"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.247l-2.04 9.608c-.153.678-.557.843-1.126.524l-3.106-2.29-1.499 1.443c-.166.166-.305.305-.624.305l.222-3.16 5.774-5.217c.251-.222-.055-.346-.388-.124L6.31 14.26l-3.06-.955c-.665-.208-.678-.665.138-.983l11.962-4.613c.553-.2 1.037.138.212.538z"/></svg>
            Contact @shipien on Telegram
          </a>
        </div>
      </div>
    </div>
  );
}
