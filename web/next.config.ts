import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  serverExternalPackages: ['@prisma/client', 'bcryptjs'],
  typescript: {
    // WASM-mode TypeScript checker crashes on Win32 with Next.js 16; IDE still checks types
    ignoreBuildErrors: true,
  },
  images: {
    remotePatterns: [],
  },
  env: {
    NEXT_PUBLIC_TELEGRAM_USERNAME: process.env.NEXT_PUBLIC_TELEGRAM_USERNAME || 'shipien',
  },
};

export default nextConfig;
