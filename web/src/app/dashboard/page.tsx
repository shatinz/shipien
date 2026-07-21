import { redirect } from 'next/navigation';
import { getSession } from '@/lib/auth';
import { prisma } from '@/lib/prisma';
import { DashboardClient } from './DashboardClient';

export const metadata = {
  title: 'Dashboard — Shipien',
  description: 'Manage your VPN subscriptions and account.',
};

export default async function DashboardPage() {
  const session = await getSession();
  if (!session) redirect('/auth/login');

  const subscriptions = await prisma.vpnSubscription.findMany({
    where: { userId: session.userId },
    include: { plan: true, receipt: true },
    orderBy: { createdAt: 'desc' },
  });

  const parsed = subscriptions.map((s) => ({
    ...s,
    plan: { ...s.plan, features: JSON.parse(s.plan.features) as string[] },
    expiresAt: s.expiresAt?.toISOString() ?? null,
    createdAt: s.createdAt.toISOString(),
  }));

  return <DashboardClient subscriptions={parsed} username={session.username} />;
}
