import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function POST(request: NextRequest) {
  const authHeader = request.headers.get('Authorization');
  const token = authHeader?.split(' ')[1];

  if (!token || token !== process.env.JWT_SECRET) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const { subscriptionId, configLink, clientName } = await request.json();

    const subscription = await prisma.vpnSubscription.findUnique({
      where: { id: subscriptionId },
      include: { plan: true },
    });

    if (!subscription) {
      return NextResponse.json({ error: 'Subscription not found' }, { status: 404 });
    }

    const expiresAt = new Date(Date.now() + subscription.plan.duration * 86400 * 1000);

    // Format config JSON to match dashboard frontend expectation
    const configData = JSON.stringify({
      links: [configLink],
      subscriptionUrl: '',
      clientName: clientName || undefined,
    });

    await prisma.$transaction([
      prisma.paymentReceipt.update({
        where: { subscriptionId },
        data: { status: 'approved' },
      }),
      prisma.vpnSubscription.update({
        where: { id: subscriptionId },
        data: {
          status: 'active',
          config: configData,
          expiresAt,
        },
      }),
    ]);

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error('Internal subscription activation error:', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
