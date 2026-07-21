import { NextRequest, NextResponse } from 'next/server';
import { getSession } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

export async function GET(request: NextRequest) {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const subscriptions = await prisma.vpnSubscription.findMany({
      where: { userId: session.userId },
      include: {
        plan: true,
        receipt: true,
      },
      orderBy: { createdAt: 'desc' },
    });

    const parsed = subscriptions.map((s) => ({
      ...s,
      plan: { ...s.plan, features: JSON.parse(s.plan.features) as string[] },
    }));

    return NextResponse.json({ subscriptions: parsed });
  } catch (err) {
    console.error('Subscriptions fetch error:', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
