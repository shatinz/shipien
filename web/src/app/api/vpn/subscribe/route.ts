import { NextRequest, NextResponse } from 'next/server';
import { getSession } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

export async function POST(request: NextRequest) {
  const session = await getSession();
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const { planId } = await request.json();

    const plan = await prisma.vpnPlan.findUnique({ where: { id: planId, active: true } });
    if (!plan) {
      return NextResponse.json({ error: 'Plan not found' }, { status: 404 });
    }

    // Create pending subscription
    const subscription = await prisma.vpnSubscription.create({
      data: {
        userId: session.userId,
        planId,
        status: 'pending',
      },
      include: { plan: true },
    });

    return NextResponse.json({ success: true, subscription });
  } catch (err) {
    console.error('Subscribe error:', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
