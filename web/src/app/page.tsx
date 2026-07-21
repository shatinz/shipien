import Link from 'next/link';
import styles from './page.module.css';

const services = [
  {
    icon: '🌐',
    title: 'Network Engineering',
    description:
      'Design, deploy, and manage enterprise-grade network infrastructure. From routing & switching to SD-WAN and zero-trust architecture.',
    tags: ['BGP', 'MPLS', 'SD-WAN', 'Zero Trust'],
    color: 'blue',
    href: '/services#network',
  },
  {
    icon: '🤖',
    title: 'AI Solutions',
    description:
      'Build intelligent systems with cutting-edge AI. From natural language processing to computer vision and predictive analytics.',
    tags: ['NLP', 'Computer Vision', 'LLMs', 'RAG'],
    color: 'purple',
    href: '/services#ai',
  },
  {
    icon: '⚙️',
    title: 'Development',
    description:
      'Full-stack software development with modern frameworks. Web apps, APIs, microservices, and cloud-native solutions.',
    tags: ['Next.js', 'Python', 'Go', 'Microservices'],
    color: 'cyan',
    href: '/services#dev',
  },
  {
    icon: '🧠',
    title: 'Machine Learning',
    description:
      'End-to-end ML pipelines: data engineering, model training, evaluation, and production deployment with MLOps best practices.',
    tags: ['PyTorch', 'MLOps', 'Feature Eng.', 'Deployment'],
    color: 'green',
    href: '/services#ml',
  },
  {
    icon: '⚡',
    title: 'Automation',
    description:
      'Eliminate repetitive work with smart automation. CI/CD pipelines, infrastructure-as-code, bots, and workflow orchestration.',
    tags: ['Terraform', 'CI/CD', 'Ansible', 'n8n'],
    color: 'orange',
    href: '/services#automation',
  },
  {
    icon: '🔒',
    title: 'VPN Services',
    description:
      'High-performance VPN with all major protocols. Log-in to see plans and purchase secure, private internet access.',
    tags: ['VLESS', 'VMess', 'Trojan', 'Hysteria2'],
    color: 'indigo',
    href: '/auth/signup',
    locked: true,
  },
];

const stats = [
  { value: '99.9%', label: 'Uptime SLA' },
  { value: '150+', label: 'Happy Clients' },
  { value: '40+', label: 'Countries' },
  { value: '24/7', label: 'Support' },
];

export default function HomePage() {
  return (
    <div className={styles.page}>
      {/* Hero */}
      <section className={styles.hero}>
        <div className={styles.heroGlow} />
        <div className="container">
          <div className={styles.heroContent}>
            <div className="badge badge-accent" style={{ marginBottom: '24px' }}>
              <span className="glow-dot" />
              All Systems Operational
            </div>
            <h1 className={styles.heroTitle}>
              The Future of
              <br />
              <span className="gradient-text">Tech Infrastructure</span>
            </h1>
            <p className={styles.heroDesc}>
              Professional network, AI, development, machine learning, and automation services —
              plus blazing-fast VPN access. Everything your digital life demands, under one roof.
            </p>
            <div className={styles.heroActions}>
              <Link href="/services" className="btn btn-primary btn-lg">
                Explore Services
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              </Link>
              <Link href="/auth/signup" className="btn btn-outline btn-lg">
                Get Started Free
              </Link>
            </div>
          </div>

          {/* Stats */}
          <div className={styles.statsRow}>
            {stats.map((s) => (
              <div key={s.label} className={styles.statCard}>
                <div className={styles.statValue}>{s.value}</div>
                <div className={styles.statLabel}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Services Grid */}
      <section className={styles.servicesSection}>
        <div className="container">
          <div className={styles.sectionHeader}>
            <div className="badge badge-accent">What We Offer</div>
            <h2 className={styles.sectionTitle}>
              Services Built for
              <span className="gradient-text"> Professionals</span>
            </h2>
            <p className={styles.sectionDesc}>
              From robust networking solutions to AI-powered automation — we've got every layer of your stack covered.
            </p>
          </div>

          <div className={styles.servicesGrid}>
            {services.map((service) => (
              <Link
                key={service.title}
                href={service.href}
                className={`${styles.serviceCard} ${styles[`color_${service.color}`]}`}
              >
                <div className={styles.serviceIcon}>{service.icon}</div>
                <div className={styles.serviceBody}>
                  <div className={styles.serviceTitleRow}>
                    <h3 className={styles.serviceTitle}>{service.title}</h3>
                    {service.locked && (
                      <span className={styles.lockBadge}>
                        🔐 Login Required
                      </span>
                    )}
                  </div>
                  <p className={styles.serviceDesc}>{service.description}</p>
                  <div className={styles.serviceTags}>
                    {service.tags.map((tag) => (
                      <span key={tag} className={styles.serviceTag}>{tag}</span>
                    ))}
                  </div>
                </div>
                <div className={styles.serviceArrow}>→</div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className={styles.ctaSection}>
        <div className="container">
          <div className={styles.ctaCard}>
            <div className={styles.ctaGlow} />
            <h2 className={styles.ctaTitle}>Ready to get started?</h2>
            <p className={styles.ctaDesc}>
              Sign up in under a minute — no credit card required. Access all services including our premium VPN.
            </p>
            <div className={styles.ctaActions}>
              <Link href="/auth/signup" className="btn btn-primary btn-lg">
                Create Free Account
              </Link>
              <a
                href={`https://t.me/${process.env.NEXT_PUBLIC_TELEGRAM_USERNAME || 'shipien'}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-outline btn-lg"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.247l-2.04 9.608c-.153.678-.557.843-1.126.524l-3.106-2.29-1.499 1.443c-.166.166-.305.305-.624.305l.222-3.16 5.774-5.217c.251-.222-.055-.346-.388-.124L6.31 14.26l-3.06-.955c-.665-.208-.678-.665.138-.983l11.962-4.613c.553-.2 1.037.138.212.538z"/></svg>
                Contact on Telegram
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <div className="container">
          <div className={styles.footerContent}>
            <div className={styles.footerBrand}>
              <div className={styles.footerLogo}>⬡ Shipien</div>
              <p className={styles.footerTagline}>Professional tech services for the modern world.</p>
            </div>
            <div className={styles.footerLinks}>
              <Link href="/services">Services</Link>
              <Link href="/auth/login">Login</Link>
              <Link href="/auth/signup">Sign Up</Link>
              <a href={`https://t.me/shipien`} target="_blank" rel="noopener noreferrer">Telegram</a>
            </div>
          </div>
          <div className={styles.footerBottom}>
            <span>© {new Date().getFullYear()} Shipien. All rights reserved.</span>
            <span>Built with ❤️ for performance</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
