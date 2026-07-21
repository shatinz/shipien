import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function POST(request: NextRequest) {
  const authHeader = request.headers.get('Authorization');
  const token = authHeader?.split(' ')[1];

  if (!token || token !== process.env.JWT_SECRET) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const { subscriptionId } = await request.json();

    const subscription = await prisma.vpnSubscription.findUnique({
      where: { id: subscriptionId },
      include: { plan: true, user: true },
    });

    if (!subscription) {
      return NextResponse.json({ error: 'Subscription not found' }, { status: 404 });
    }

    const planFeatures = JSON.parse(subscription.plan.features) as string[];

    let configName: string | undefined = undefined;
    if (subscription.config) {
      try {
        const parsed = JSON.parse(subscription.config);
        configName = parsed.configName;
      } catch {}
    }

    return NextResponse.json({
      success: true,
      subscription: {
        id: subscription.id,
        status: subscription.status,
        duration: subscription.plan.duration,
        bandwidth: subscription.plan.bandwidth,
        username: subscription.user.username,
        phone: subscription.user.phone,
        planName: subscription.plan.name,
        configName,
      },
    });
  } catch (err) {
    console.error('Internal subscription fetch error:', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
