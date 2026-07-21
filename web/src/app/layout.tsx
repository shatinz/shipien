import type { Metadata } from 'next';
import Script from 'next/script';
import './globals.css';
import { Navbar } from '@/components/Navbar';

export const metadata: Metadata = {
  title: 'Shipien — AI, Network & VPN Services',
  description:
    'Professional network engineering, AI development, machine learning, automation, and secure VPN services. Built for teams and individuals who demand performance.',
  keywords: ['VPN', 'AI', 'network', 'machine learning', 'automation', 'dev', 'Shipien'],
  openGraph: {
    title: 'Shipien — AI, Network & VPN Services',
    description: 'Professional tech services: AI, Network, Dev, ML, Automation, VPN',
    type: 'website',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="grid-bg">
        <Script src="https://telegram.org/js/telegram-web-app.js" strategy="beforeInteractive" />
        <Navbar />
        <main>{children}</main>
      </body>
    </html>
  );
}
