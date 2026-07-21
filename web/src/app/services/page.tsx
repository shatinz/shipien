import styles from './services.module.css';

export const metadata = {
  title: 'Services — Shipien',
  description: 'Network engineering, AI, development, machine learning, automation, and VPN services.',
};

const services = [
  {
    id: 'network',
    icon: '🌐',
    title: 'Network Engineering',
    tagline: 'Enterprise-grade networking solutions',
    color: 'blue',
    description:
      'We design, deploy, and manage robust network infrastructure tailored for enterprise demands. From initial architecture to day-2 operations, we handle every layer of your network stack.',
    capabilities: [
      'BGP & OSPF routing design and optimization',
      'SD-WAN deployment (Cisco Viptela, VeloCloud)',
      'MPLS and L3VPN configurations',
      'Zero-Trust Network Architecture (ZTNA)',
      'Network monitoring and observability (Prometheus, Grafana)',
      'Firewall and IDS/IPS deployment',
      'Load balancing and HA cluster design',
      'Network automation with Ansible & Python',
    ],
    tech: ['Cisco', 'Juniper', 'Palo Alto', 'Ansible', 'Python', 'Prometheus', 'BGP', 'SD-WAN'],
  },
  {
    id: 'ai',
    icon: '🤖',
    title: 'AI Solutions',
    tagline: 'Intelligent systems powered by modern AI',
    color: 'purple',
    description:
      'Build cutting-edge AI applications using the latest LLMs, vision models, and ML techniques. We help you go from idea to production with robust, scalable AI pipelines.',
    capabilities: [
      'LLM fine-tuning and RAG pipelines',
      'Natural Language Processing (NLP) systems',
      'Computer vision and image recognition',
      'Conversational AI / chatbot development',
      'AI agent and multi-agent systems',
      'Document intelligence and OCR',
      'Recommendation engines',
      'Prompt engineering and evaluation',
    ],
    tech: ['OpenAI', 'Llama', 'LangChain', 'HuggingFace', 'PyTorch', 'FastAPI', 'Pinecone', 'RAG'],
  },
  {
    id: 'dev',
    icon: '⚙️',
    title: 'Software Development',
    tagline: 'Modern full-stack engineering',
    color: 'cyan',
    description:
      'End-to-end software development services — from frontend interfaces to backend APIs and cloud-native microservices. We ship quality code that scales.',
    capabilities: [
      'Web application development (Next.js, React)',
      'REST and GraphQL API design',
      'Microservices and event-driven architecture',
      'Database design and optimization',
      'Mobile-responsive UI/UX implementation',
      'Authentication and authorization systems',
      'Real-time features (WebSocket, SSE)',
      'Cloud-native deployment (Docker, Kubernetes)',
    ],
    tech: ['Next.js', 'React', 'Python', 'Go', 'Node.js', 'PostgreSQL', 'Redis', 'Docker'],
  },
  {
    id: 'ml',
    icon: '🧠',
    title: 'Machine Learning',
    tagline: 'End-to-end ML pipelines and MLOps',
    color: 'green',
    description:
      'From raw data to deployed models — we build complete ML systems with data engineering, model training, evaluation, and production deployment using MLOps best practices.',
    capabilities: [
      'Data collection, cleaning, and feature engineering',
      'Supervised and unsupervised model training',
      'Time-series forecasting and anomaly detection',
      'Model evaluation, A/B testing, and explainability',
      'MLflow experiment tracking and model registry',
      'CI/CD for ML pipelines',
      'Model serving with FastAPI and TorchServe',
      'Edge deployment optimization (ONNX, TFLite)',
    ],
    tech: ['PyTorch', 'scikit-learn', 'MLflow', 'Airflow', 'DVC', 'Spark', 'ONNX', 'Kubernetes'],
  },
  {
    id: 'automation',
    icon: '⚡',
    title: 'Automation',
    tagline: 'Eliminate repetitive work at scale',
    color: 'orange',
    description:
      'Smart automation solutions that save time and reduce human error. From infrastructure provisioning to workflow orchestration, we automate the tedious so your team can focus on what matters.',
    capabilities: [
      'Infrastructure-as-Code with Terraform & Pulumi',
      'CI/CD pipeline design (GitHub Actions, GitLab CI)',
      'Configuration management with Ansible',
      'Workflow automation (n8n, Zapier, custom)',
      'Telegram and Discord bot development',
      'Scheduled job orchestration',
      'API integration and data pipeline automation',
      'Alert and incident response automation',
    ],
    tech: ['Terraform', 'Ansible', 'GitHub Actions', 'n8n', 'Python', 'Bash', 'Docker', 'GitLab'],
  },
];

export default function ServicesPage() {
  return (
    <div className={styles.page}>
      <div className={styles.heroGlow} />
      <div className="container">
        {/* Header */}
        <div className={styles.header}>
          <div className="badge badge-accent">Our Services</div>
          <h1 className={styles.title}>
            Everything You Need,<br />
            <span className="gradient-text">Under One Roof</span>
          </h1>
          <p className={styles.subtitle}>
            From network infrastructure to AI models to automation scripts — we provide
            end-to-end professional tech services.
          </p>
        </div>

        {/* Services */}
        <div className={styles.servicesList}>
          {services.map((s, i) => (
            <div
              key={s.id}
              id={s.id}
              className={`${styles.serviceRow} ${i % 2 === 1 ? styles.reversed : ''}`}
            >
              <div className={styles.serviceInfo}>
                <div className={`${styles.serviceIconWrap} ${styles[`color_${s.color}`]}`}>
                  <span>{s.icon}</span>
                </div>
                <div className={styles.serviceTagline}>{s.tagline}</div>
                <h2 className={styles.serviceTitle}>{s.title}</h2>
                <p className={styles.serviceDesc}>{s.description}</p>
                <div className={styles.techTags}>
                  {s.tech.map((t) => (
                    <span key={t} className={styles.techTag}>{t}</span>
                  ))}
                </div>
              </div>

              <div className={styles.capabilityCard}>
                <p className={styles.capTitle}>Capabilities</p>
                <ul className={styles.capList}>
                  {s.capabilities.map((c) => (
                    <li key={c}>
                      <span className={styles.capDot} />
                      {c}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>

        {/* VPN teaser */}
        <div className={styles.vpnTeaser}>
          <div className={styles.vpnTeaserContent}>
            <span style={{ fontSize: '40px' }}>🔒</span>
            <div>
              <h3>VPN Services</h3>
              <p>High-performance VPN with all major protocols. Log in to see plans and purchase.</p>
            </div>
          </div>
          <a href="/auth/signup" className="btn btn-primary">
            Sign Up to Access VPN →
          </a>
        </div>
      </div>
    </div>
  );
}
