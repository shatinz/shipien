import { redirect } from 'next/navigation';
import { getSession } from '@/lib/auth';
import { prisma } from '@/lib/prisma';
import { VpnPageClient } from './VpnPageClient';

export const metadata = {
  title: 'VPN Plans — Shipien',
  description: 'Choose your VPN plan and get secure, high-speed internet access.',
};

export default async function VpnPage() {
  const session = await getSession();
  if (!session) redirect('/auth/login');

  const plans = await prisma.vpnPlan.findMany({
    where: { active: true },
    orderBy: { sortOrder: 'asc' },
  });

  const parsedPlans = plans.map((p) => ({
    ...p,
    features: JSON.parse(p.features) as string[],
  }));

  return <VpnPageClient plans={parsedPlans} username={session.username} />;
}
